from __future__ import annotations

import time
from collections.abc import Callable
from typing import TypeVar

from .exceptions import ProviderRetryableError

T = TypeVar("T")


def retry_call(
    fn: Callable[[], T],
    *,
    max_retries: int = 2,
    delay_seconds: float = 0.3,
) -> T:
    last_exc: Exception | None = None

    for attempt in range(max_retries + 1):
        try:
            return fn()
        except ProviderRetryableError as exc:
            last_exc = exc
            if attempt >= max_retries:
                break
            time.sleep(delay_seconds)

    if last_exc:
        raise last_exc

    raise RuntimeError("retry_call failed without exception")