from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping


def parse_env_bool(value: object, default: bool = False) -> bool:
    if value is None:
        return bool(default)
    normalized = str(value).strip().lower()
    if normalized in {"1", "true", "yes", "on", "enabled"}:
        return True
    if normalized in {"0", "false", "no", "off", "disabled", ""}:
        return False
    return bool(default)


def bounded_env_int(
    name: str,
    default: int,
    minimum: int,
    maximum: int,
    *,
    environ: Mapping[str, str] | None = None,
) -> int:
    source = os.environ if environ is None else environ
    try:
        parsed = int(str(source.get(name, str(default))).strip())
    except (TypeError, ValueError):
        parsed = int(default)
    return max(int(minimum), min(parsed, int(maximum)))


def resolve_runtime_path(base_dir: Path, value: object, default: Path) -> Path:
    raw = str(value or "").strip()
    candidate = Path(raw).expanduser() if raw else default
    if not candidate.is_absolute():
        candidate = base_dir / candidate
    return candidate.resolve(strict=False)


@dataclass(frozen=True, slots=True)
class WebhookSettings:
    enabled: bool
    bind_host: str
    local_port: int
    max_body_bytes: int
    max_batch_events: int
    tunnel_retry_seconds: int
    public_base_url: str
    secret_value: str
    secret_file: Path
    ngrok_auth_token: str
    ngrok_domain: str
    ngrok_region: str


@dataclass(frozen=True, slots=True)
class RuntimeSettings:
    base_dir: Path
    database_path: Path
    maintenance_path: Path
    mongodb_uri_file: Path
    secret_store_dir: Path
    webhook: WebhookSettings

    @classmethod
    def from_env(
        cls,
        base_dir: Path,
        *,
        environ: Mapping[str, str] | None = None,
    ) -> "RuntimeSettings":
        source = os.environ if environ is None else environ
        root = Path(base_dir).resolve(strict=False)
        webhook = WebhookSettings(
            enabled=parse_env_bool(source.get("WEBHOOK_ENABLED"), True),
            bind_host=str(source.get("WEBHOOK_BIND_HOST", "127.0.0.1")).strip()
            or "127.0.0.1",
            local_port=bounded_env_int("WEBHOOK_LOCAL_PORT", 8090, 1024, 65535, environ=source),
            max_body_bytes=bounded_env_int("WEBHOOK_MAX_BODY_BYTES", 65536, 4096, 1048576, environ=source),
            max_batch_events=bounded_env_int("WEBHOOK_MAX_BATCH_EVENTS", 100, 1, 1000, environ=source),
            tunnel_retry_seconds=bounded_env_int("WEBHOOK_TUNNEL_RETRY_SECONDS", 300, 30, 3600, environ=source),
            public_base_url=str(source.get("WEBHOOK_PUBLIC_BASE_URL", "")).strip(),
            secret_value=str(source.get("WEBHOOK_SECRET", "")).strip(),
            secret_file=resolve_runtime_path(root, source.get("WEBHOOK_SECRET_FILE"), root / ".runtime" / "webhook_secret"),
            ngrok_auth_token=str(source.get("NGROK_AUTHTOKEN") or source.get("NGROK_AUTH_TOKEN") or "").strip(),
            ngrok_domain=str(source.get("NGROK_DOMAIN", "")).strip(),
            ngrok_region=str(source.get("NGROK_REGION", "")).strip(),
        )
        return cls(
            base_dir=root,
            database_path=resolve_runtime_path(root, source.get("DB_PATH"), root / "bot_database.db"),
            maintenance_path=resolve_runtime_path(root, source.get("KODO_MAINTENANCE_PATH"), root / ".kodo_maintenance.json"),
            mongodb_uri_file=resolve_runtime_path(root, source.get("MONGODB_URI_FILE"), root / ".runtime" / "mongodb_uri"),
            secret_store_dir=resolve_runtime_path(root, source.get("SECRET_STORE_DIR"), root / ".runtime" / "secrets"),
            webhook=webhook,
        )


__all__ = ["RuntimeSettings", "WebhookSettings", "bounded_env_int", "parse_env_bool", "resolve_runtime_path"]
