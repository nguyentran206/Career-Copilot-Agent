from threading import BoundedSemaphore, Lock
from types import SimpleNamespace

import pytest

from app.schemas.analysis import ParsedCV, ParsedJD
from app.services.gemini import (
    GeminiParsedCV,
    GeminiParsedJD,
    GeminiRateLimitCooldownError,
    GeminiService,
    _fallback_warnings,
)


def _service_returning(value):
    service = object.__new__(GeminiService)
    service._structured = lambda prompt, schema: (value, [])
    return service


def test_gemini_jd_extraction_schema_does_not_contain_business_weight_constraints():
    schema = GeminiParsedJD.model_json_schema()
    serialized = str(schema)

    assert "base_weight" not in serialized
    assert "exclusiveMinimum" not in serialized


def test_parse_jd_maps_extraction_to_domain_and_calculates_base_weight():
    extracted = GeminiParsedJD(
        language_info={
            "primary_language": "vi",
            "detected_languages": ["vi"],
            "confidence": 0.98,
        },
        job_title={
            "source_name": "Chuyên viên phân tích dữ liệu",
            "canonical_name_en": "Data Analyst",
        },
        skill_requirements=[
            {
                "source_name": "SQL",
                "canonical_name_en": "SQL",
                "classification": "required",
                "critical": True,
                "source_evidence": "Bắt buộc sử dụng SQL.",
                "canonical_evidence_en": "SQL is required.",
            },
            {
                "source_name": "Power BI",
                "canonical_name_en": "Power BI",
                "classification": "preferred",
                "source_evidence": "Ưu tiên Power BI.",
                "canonical_evidence_en": "Power BI is preferred.",
            },
        ],
    )

    result = _service_returning(extracted).parse_jd("Vietnamese JD source text")

    assert isinstance(result.value, ParsedJD)
    assert result.warnings == []
    assert result.value.required_skills == ["SQL"]
    assert result.value.preferred_skills == ["Power BI"]
    assert result.value.skill_requirements[0].base_weight == 1.0
    assert result.value.skill_requirements[1].base_weight == 0.65
    assert result.value.skill_requirements[0].evidence == "SQL is required."


def test_parse_cv_maps_extraction_and_clamps_language_confidence():
    extracted = GeminiParsedCV(
        language_info={
            "primary_language": "en",
            "detected_languages": ["en"],
            "confidence": 1.2,
        },
        skills=[{"source_name": "Python", "canonical_name_en": "Python"}],
        evidence=[
            {
                "kind": "experience",
                "source_text": "Built a Python API.",
                "source_language": "en",
                "canonical_summary_en": "Built a Python API.",
            }
        ],
    )

    result = _service_returning(extracted).parse_cv("English CV source text")

    assert isinstance(result.value, ParsedCV)
    assert result.warnings == []
    assert result.value.skills == ["Python"]
    assert result.value.language_info.confidence == 1.0


def test_rate_limit_error_adds_actionable_provider_warning():
    error = RuntimeError("request failed")
    error.code = 429
    error.status = "RESOURCE_EXHAUSTED"

    assert _fallback_warnings("GEMINI_GENERATION_FALLBACK", error) == [
        "GEMINI_GENERATION_FALLBACK",
        "GEMINI_RATE_LIMITED",
    ]


def test_rate_limit_opens_circuit_and_blocks_follow_up_provider_call():
    calls = []

    class RateLimitError(RuntimeError):
        code = 429

    class Models:
        def generate_content(self, **kwargs):
            calls.append(kwargs)
            raise RateLimitError("rate limited")

    service = object.__new__(GeminiService)
    service._rate_limit_cooldown_seconds = 60.0
    service._rate_limited_until = 0.0
    service._state_lock = Lock()
    service._request_slots = BoundedSemaphore(1)
    service._model = "test-model"
    service._fallback_model = None
    service._max_server_retries = 0
    service._retry_backoff_seconds = 0.0
    service._client = SimpleNamespace(models=Models())
    service._types = SimpleNamespace(
        GenerateContentConfig=lambda **kwargs: kwargs
    )

    with pytest.raises(RateLimitError):
        service._structured("prompt", GeminiParsedCV)

    with pytest.raises(GeminiRateLimitCooldownError):
        service._structured("prompt", GeminiParsedCV)

    assert len(calls) == 1


def test_server_error_retries_then_uses_fallback_model():
    calls = []

    class ServerError(RuntimeError):
        code = 503

    class Models:
        def generate_content(self, model, contents, config):
            calls.append(model)
            if model == "primary-model":
                raise ServerError("high demand")
            return SimpleNamespace(text="ok", parsed=None)

    service = object.__new__(GeminiService)
    service._rate_limit_cooldown_seconds = 60.0
    service._rate_limited_until = 0.0
    service._state_lock = Lock()
    service._request_slots = BoundedSemaphore(1)
    service._model = "primary-model"
    service._fallback_model = "fallback-model"
    service._max_server_retries = 1
    service._retry_backoff_seconds = 0.0
    service._client = SimpleNamespace(models=Models())

    response, warnings = service._generate_content("prompt", {})

    assert response.text == "ok"
    assert calls == ["primary-model", "fallback-model"]
    assert warnings == ["GEMINI_MODEL_FALLBACK_USED"]
