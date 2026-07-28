from collections import defaultdict, deque
from math import ceil
from threading import RLock
from time import monotonic

from app.core.config import settings


class RequestLimitExceeded(RuntimeError):
    def __init__(self, code: str, message: str, retry_after: int) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.retry_after = max(1, retry_after)


class AnalyzeRequestLimiter:
    def __init__(self) -> None:
        self._requests: dict[str, deque[float]] = defaultdict(deque)
        self._active = 0
        self._lock = RLock()
        self._last_cleanup = monotonic()

    def reserve(self, client_key: str) -> None:
        now = monotonic()
        window = settings.analyze_rate_limit_window_seconds
        with self._lock:
            if now - self._last_cleanup >= window:
                for key in list(self._requests):
                    entries = self._requests[key]
                    while entries and entries[0] <= now - window:
                        entries.popleft()
                    if not entries:
                        del self._requests[key]
                self._last_cleanup = now
            requests = self._requests[client_key]
            while requests and requests[0] <= now - window:
                requests.popleft()
            if len(requests) >= settings.analyze_rate_limit_requests:
                retry_after = ceil(window - (now - requests[0]))
                raise RequestLimitExceeded(
                    "ANALYZE_RATE_LIMITED",
                    "Too many analysis requests. Please retry later.",
                    retry_after,
                )
            if self._active >= settings.max_concurrent_analyses:
                raise RequestLimitExceeded(
                    "ANALYSIS_CAPACITY_REACHED",
                    "All analysis slots are busy. Please retry shortly.",
                    5,
                )
            requests.append(now)
            self._active += 1

    def release(self) -> None:
        with self._lock:
            self._active = max(0, self._active - 1)

    def clear(self) -> None:
        with self._lock:
            self._requests.clear()
            self._active = 0
            self._last_cleanup = monotonic()


analyze_request_limiter = AnalyzeRequestLimiter()
