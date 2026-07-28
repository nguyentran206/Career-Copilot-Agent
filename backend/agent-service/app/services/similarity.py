import math
from difflib import SequenceMatcher
from threading import Lock
import time
from typing import Protocol


class SimilarityProvider(Protocol):
    def prepare(self, texts: list[str]) -> list[str]:
        ...

    def similarity(self, left: str, right: str) -> float:
        ...


class LexicalSimilarityProvider:
    def prepare(self, texts: list[str]) -> list[str]:
        return []

    def similarity(self, left: str, right: str) -> float:
        left_normalized = " ".join(left.lower().split())
        right_normalized = " ".join(right.lower().split())
        return SequenceMatcher(None, left_normalized, right_normalized).ratio()


class FallbackSimilarityProvider:
    def __init__(
        self,
        primary: SimilarityProvider,
        fallback: SimilarityProvider,
        retry_after_seconds: float = 60.0,
    ) -> None:
        self._primary = primary
        self._fallback = fallback
        self._primary_available = True
        self._primary_unavailable_until = 0.0
        self._retry_after_seconds = retry_after_seconds

    def prepare(self, texts: list[str]) -> list[str]:
        if time.monotonic() >= self._primary_unavailable_until:
            self._primary_available = True
        if not self._primary_available:
            return ["GEMINI_EMBEDDING_FALLBACK"]
        try:
            return self._primary.prepare(texts)
        except Exception as exc:
            self._primary_available = False
            self._primary_unavailable_until = (
                time.monotonic() + self._retry_after_seconds
            )
            warnings = ["GEMINI_EMBEDDING_FALLBACK"]
            code = getattr(exc, "code", None)
            if code == 429:
                warnings.append("GEMINI_RATE_LIMITED")
            elif code in {401, 403}:
                warnings.append("GEMINI_AUTH_FAILED")
            elif code == 404:
                warnings.append("GEMINI_MODEL_UNAVAILABLE")
            elif isinstance(code, int) and code >= 500:
                warnings.append("GEMINI_SERVER_ERROR")
            return warnings

    def similarity(self, left: str, right: str) -> float:
        if not self._primary_available:
            return self._fallback.similarity(left, right)
        try:
            return self._primary.similarity(left, right)
        except Exception:
            self._primary_available = False
            self._primary_unavailable_until = (
                time.monotonic() + self._retry_after_seconds
            )
            return self._fallback.similarity(left, right)


class GeminiEmbeddingRateLimitCooldownError(RuntimeError):
    code = 429


class GeminiEmbeddingSimilarityProvider:
    def __init__(
        self,
        api_key: str,
        model: str,
        timeout_seconds: float = 30.0,
        rate_limit_cooldown_seconds: float = 60.0,
    ) -> None:
        from google import genai
        from google.genai import types

        self._client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(timeout=int(timeout_seconds * 1000)),
        )
        self._model = model
        self._cache: dict[str, list[float]] = {}
        self._rate_limit_cooldown_seconds = rate_limit_cooldown_seconds
        self._rate_limited_until = 0.0
        self._lock = Lock()

    @staticmethod
    def _cache_key(text: str) -> str:
        return " ".join(text.lower().split())

    def prepare(self, texts: list[str]) -> list[str]:
        unique_texts: dict[str, str] = {}
        for text in texts:
            cleaned = " ".join(text.split())
            if cleaned:
                unique_texts.setdefault(self._cache_key(cleaned), cleaned)
        with self._lock:
            if time.monotonic() < self._rate_limited_until:
                raise GeminiEmbeddingRateLimitCooldownError(
                    "Gemini embedding requests are in cooldown."
                )
            missing = [
                (key, text)
                for key, text in unique_texts.items()
                if key not in self._cache
            ]
            if not missing:
                return []
            try:
                result = self._client.models.embed_content(
                    model=self._model,
                    contents=[text for _, text in missing],
                )
            except Exception as exc:
                if getattr(exc, "code", None) == 429:
                    self._rate_limited_until = max(
                        self._rate_limited_until,
                        time.monotonic() + self._rate_limit_cooldown_seconds,
                    )
                raise
            if not result.embeddings or len(result.embeddings) != len(missing):
                raise ValueError("Gemini returned an incomplete embedding batch.")
            for (key, _), embedding in zip(missing, result.embeddings):
                if not embedding.values:
                    raise ValueError("Gemini returned no embedding values.")
                self._cache[key] = list(embedding.values)
        return []

    def _embed(self, text: str) -> list[float]:
        cache_key = self._cache_key(text)
        if cache_key not in self._cache:
            self.prepare([text])
        return self._cache[cache_key]

    def similarity(self, left: str, right: str) -> float:
        left_vector = self._embed(left)
        right_vector = self._embed(right)
        numerator = sum(a * b for a, b in zip(left_vector, right_vector))
        left_norm = math.sqrt(sum(value * value for value in left_vector))
        right_norm = math.sqrt(sum(value * value for value in right_vector))
        if left_norm == 0 or right_norm == 0:
            return 0.0
        return max(0.0, min(1.0, numerator / (left_norm * right_norm)))
