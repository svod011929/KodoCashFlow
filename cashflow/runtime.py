from __future__ import annotations

import json
import os
import socket
import uuid
from datetime import datetime, timezone
from pathlib import Path

try:
    import fcntl
except ImportError:  # pragma: no cover
    fcntl = None


class ProcessSingleton:
    """Prevent two bot processes from using the same database concurrently."""

    def __init__(self, path: str | Path, *, version: int):
        self.path = Path(path)
        self.version = int(version)
        self.handle = None
        self.fallback_fd = None

    def acquire(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if fcntl is not None:
            self.handle = open(self.path, "a+", encoding="utf-8")
            try:
                fcntl.flock(self.handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError as exc:
                self.handle.seek(0)
                owner = self.handle.read().strip() or "unknown process"
                self.handle.close()
                self.handle = None
                raise RuntimeError(f"Another bot instance is already running ({owner}). Lock: {self.path}") from exc
            self.handle.seek(0)
            self.handle.truncate()
            self.handle.write(json.dumps({"pid": os.getpid(), "host": socket.gethostname(), "version": self.version, "started_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")}, ensure_ascii=False))
            self.handle.flush()
            return
        try:
            self.fallback_fd = os.open(str(self.path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError as exc:
            raise RuntimeError(f"Another instance lock exists: {self.path}") from exc
        os.write(self.fallback_fd, f"pid={os.getpid()} host={socket.gethostname()} version={self.version}".encode())

    def release(self) -> None:
        if self.handle is not None:
            try:
                if fcntl is not None:
                    fcntl.flock(self.handle.fileno(), fcntl.LOCK_UN)
            finally:
                self.handle.close()
                self.handle = None
            return
        if self.fallback_fd is not None:
            try:
                os.close(self.fallback_fd)
            finally:
                self.fallback_fd = None
                try:
                    self.path.unlink()
                except FileNotFoundError:
                    pass


def build_runtime_instance_id() -> str:
    return f"{socket.gethostname()}:{os.getpid()}:{uuid.uuid4().hex[:12]}"
