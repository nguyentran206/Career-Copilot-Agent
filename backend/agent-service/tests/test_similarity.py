from threading import Lock
from types import SimpleNamespace

from app.services.similarity import GeminiEmbeddingSimilarityProvider


def test_gemini_embedding_provider_batches_unique_texts_and_reuses_cache():
    calls = []

    class Models:
        def embed_content(self, model, contents):
            calls.append((model, contents))
            vectors = {
                "Python": [1.0, 0.0],
                "SQL": [0.0, 1.0],
                "Data Analysis": [0.8, 0.2],
            }
            return SimpleNamespace(
                embeddings=[
                    SimpleNamespace(values=vectors[text]) for text in contents
                ]
            )

    provider = object.__new__(GeminiEmbeddingSimilarityProvider)
    provider._client = SimpleNamespace(models=Models())
    provider._model = "embedding-test-model"
    provider._cache = {}
    provider._rate_limit_cooldown_seconds = 60.0
    provider._rate_limited_until = 0.0
    provider._lock = Lock()

    provider.prepare(["Python", "SQL", "Python", "Data Analysis"])
    provider.prepare(["SQL", "Python"])

    assert len(calls) == 1
    assert calls[0][1] == ["Python", "SQL", "Data Analysis"]
    assert provider.similarity("Python", "Python") == 1.0
    assert 0.0 < provider.similarity("Python", "Data Analysis") < 1.0
