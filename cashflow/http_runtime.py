from __future__ import annotations

import asyncio
import json
import os
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator


def _bounded_env_int(name: str, default: int, minimum: int, maximum: int) -> int:
    try:
        value = int(str(os.getenv(name, default)).strip())
    except (TypeError, ValueError):
        value = int(default)
    return max(int(minimum), min(int(value), int(maximum)))


HTTP_GLOBAL_CONCURRENCY = _bounded_env_int("HTTP_GLOBAL_CONCURRENCY", 16, 1, 128)
HTTP_CRITICAL_CONCURRENCY = _bounded_env_int("HTTP_CRITICAL_CONCURRENCY", 4, 1, 32)
HTTP_RESPONSE_MAX_BYTES = _bounded_env_int("HTTP_RESPONSE_MAX_BYTES", 1_000_000, 4096, 8_000_000)
PROVIDER_CONNECTOR_LIMIT = _bounded_env_int("PROVIDER_CONNECTOR_LIMIT", 5, 1, 30)

_GLOBAL_GATE = asyncio.Semaphore(HTTP_GLOBAL_CONCURRENCY)
_CRITICAL_GATE = asyncio.Semaphore(HTTP_CRITICAL_CONCURRENCY)
_global_in_flight = 0
_global_waiters = 0
_critical_in_flight = 0
_critical_waiters = 0


class ResponseTooLargeError(ValueError):
    pass


@asynccontextmanager
async def http_slot(*, critical: bool = False) -> AsyncIterator[None]:
    global _global_in_flight, _global_waiters, _critical_in_flight, _critical_waiters
    gate = _CRITICAL_GATE if critical else _GLOBAL_GATE
    if critical:
        _critical_waiters += 1
    else:
        _global_waiters += 1
    try:
        await gate.acquire()
    finally:
        if critical:
            _critical_waiters = max(0, _critical_waiters - 1)
        else:
            _global_waiters = max(0, _global_waiters - 1)
    if critical:
        _critical_in_flight += 1
    else:
        _global_in_flight += 1
    try:
        yield
    finally:
        if critical:
            _critical_in_flight = max(0, _critical_in_flight - 1)
        else:
            _global_in_flight = max(0, _global_in_flight - 1)
        gate.release()


async def read_limited_body(response: Any, *, max_bytes: int = HTTP_RESPONSE_MAX_BYTES) -> bytes:
    limit = max(1, int(max_bytes))
    content_length = getattr(response, "content_length", None)
    if content_length is not None and int(content_length) > limit:
        raise ResponseTooLargeError(f"HTTP response exceeds {limit} bytes")
    try:
        raw = await response.content.readexactly(limit + 1)
    except asyncio.IncompleteReadError as exc:
        raw = exc.partial
    if len(raw) > limit:
        raise ResponseTooLargeError(f"HTTP response exceeds {limit} bytes")
    return raw


async def read_limited_text(response: Any, *, max_bytes: int = HTTP_RESPONSE_MAX_BYTES) -> str:
    raw = await read_limited_body(response, max_bytes=max_bytes)
    encoding = getattr(response, "charset", None) or "utf-8"
    try:
        return raw.decode(encoding, errors="replace")
    except LookupError:
        return raw.decode("utf-8", errors="replace")


async def read_limited_json(response: Any, *, max_bytes: int = HTTP_RESPONSE_MAX_BYTES) -> Any:
    raw_text = await read_limited_text(response, max_bytes=max_bytes)
    return json.loads(raw_text) if raw_text else {}


def http_runtime_metrics() -> dict[str, int]:
    return {"global_limit": HTTP_GLOBAL_CONCURRENCY, "global_in_flight": _global_in_flight, "global_waiters": _global_waiters, "critical_limit": HTTP_CRITICAL_CONCURRENCY, "critical_in_flight": _critical_in_flight, "critical_waiters": _critical_waiters}


@asynccontextmanager
async def limited_request(session: Any, method: str, url: str, *, critical: bool = False, **kwargs: Any) -> AsyncIterator[Any]:
    async with http_slot(critical=critical):
        async with session.request(method, url, **kwargs) as response:
            yield response
