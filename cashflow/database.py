from __future__ import annotations

import asyncio
from collections.abc import Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, AsyncIterator

import aiosqlite

DatabasePath = str | Path | Callable[[], str | Path]


@dataclass(frozen=True, slots=True)
class SQLiteOptions:
    busy_timeout_ms: int = 15_000
    max_concurrency: int = 4
    cache_kib: int = 1_024
    temp_store: str = "FILE"

    def __post_init__(self) -> None:
        if self.busy_timeout_ms < 1:
            raise ValueError("busy_timeout_ms must be positive")
        if self.max_concurrency < 1:
            raise ValueError("max_concurrency must be positive")
        if self.cache_kib < 1:
            raise ValueError("cache_kib must be positive")
        if self.temp_store not in {"FILE", "MEMORY"}:
            raise ValueError("temp_store must be FILE or MEMORY")


class SQLiteDatabase:
    """Own SQLite connection policy and expose bounded runtime metrics."""

    def __init__(self, path: DatabasePath, options: SQLiteOptions) -> None:
        self._path = path
        self.options = options
        self._gate = asyncio.Semaphore(options.max_concurrency)
        self._checked_out = 0
        self._waiters = 0

    @property
    def path(self) -> str:
        value = self._path() if callable(self._path) else self._path
        return str(Path(value))

    @property
    def metrics(self) -> dict[str, int]:
        return {"checked_out": self._checked_out, "waiters": self._waiters, "max_concurrency": self.options.max_concurrency}

    @asynccontextmanager
    async def connect(self, *, row_factory: Any | None = None) -> AsyncIterator[aiosqlite.Connection]:
        acquired = False
        connection: aiosqlite.Connection | None = None
        self._waiters += 1
        try:
            await self._gate.acquire()
            acquired = True
        finally:
            self._waiters = max(0, self._waiters - 1)
        self._checked_out += 1
        try:
            connection = await aiosqlite.connect(self.path, timeout=self.options.busy_timeout_ms / 1_000)
            await connection.execute("PRAGMA foreign_keys = ON")
            await connection.execute(f"PRAGMA busy_timeout = {self.options.busy_timeout_ms}")
            await connection.execute("PRAGMA synchronous = NORMAL")
            await connection.execute(f"PRAGMA cache_size = -{self.options.cache_kib}")
            await connection.execute(f"PRAGMA temp_store = {self.options.temp_store}")
            if row_factory is not None:
                connection.row_factory = row_factory
            yield connection
        finally:
            if connection is not None:
                await connection.close()
            self._checked_out = max(0, self._checked_out - 1)
            if acquired:
                self._gate.release()


__all__ = ["DatabasePath", "SQLiteDatabase", "SQLiteOptions"]
