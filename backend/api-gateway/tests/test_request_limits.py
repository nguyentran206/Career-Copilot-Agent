import pytest

from app.core.request_limits import AnalyzeRequestLimiter, RequestLimitExceeded


def test_per_client_rate_limit_returns_retry_after(monkeypatch):
    monkeypatch.setattr("app.core.request_limits.settings.analyze_rate_limit_requests", 2)
    monkeypatch.setattr("app.core.request_limits.settings.max_concurrent_analyses", 10)
    limiter = AnalyzeRequestLimiter()
    limiter.reserve("client-a")
    limiter.release()
    limiter.reserve("client-a")
    limiter.release()

    with pytest.raises(RequestLimitExceeded) as exc_info:
        limiter.reserve("client-a")

    assert exc_info.value.code == "ANALYZE_RATE_LIMITED"
    assert exc_info.value.retry_after >= 1
