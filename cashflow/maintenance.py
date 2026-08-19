from __future__ import annotations

import html
import json
import os
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=path.name + '.', suffix='.tmp', dir=str(path.parent))
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    finally:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass


@dataclass
class MaintenanceController:
    """File-backed maintenance flag that survives database swaps."""

    path: Path

    def __init__(self, path: str | os.PathLike[str]):
        self.path = Path(path)

    def snapshot(self) -> dict[str, Any]:
        default = {'enabled': False, 'reason': '', 'enabled_at': None, 'enabled_by': None, 'updated_at': None}
        if not self.path.exists():
            return default
        try:
            raw = json.loads(self.path.read_text(encoding='utf-8'))
        except Exception:
            result = dict(default)
            result['enabled'] = True
            result['reason'] = 'Состояние технических работ повреждено. Администратору необходимо проверить служебный файл.'
            result['corrupt'] = True
            return result
        result = dict(default)
        if isinstance(raw, dict):
            result.update(raw)
        result['enabled'] = bool(result.get('enabled'))
        result['reason'] = str(result.get('reason') or '')[:1000]
        return result

    def is_active(self) -> bool:
        return bool(self.snapshot().get('enabled'))

    def enable(self, *, reason: str = '', actor_id: int | None = None) -> dict[str, Any]:
        now = _utc_now()
        payload = {'enabled': True, 'reason': str(reason or 'Проводятся технические работы.')[:1000], 'enabled_at': now, 'enabled_by': None if actor_id is None else int(actor_id), 'updated_at': now}
        _atomic_write_json(self.path, payload)
        return payload

    def disable(self, *, actor_id: int | None = None) -> dict[str, Any]:
        previous = self.snapshot()
        payload = {'enabled': False, 'reason': str(previous.get('reason') or ''), 'enabled_at': previous.get('enabled_at'), 'enabled_by': previous.get('enabled_by'), 'disabled_by': None if actor_id is None else int(actor_id), 'updated_at': _utc_now()}
        _atomic_write_json(self.path, payload)
        return payload

    def set_reason(self, reason: str, *, actor_id: int | None = None) -> dict[str, Any]:
        current = self.snapshot()
        current.pop('corrupt', None)
        current['reason'] = str(reason or '')[:1000]
        current['updated_at'] = _utc_now()
        current['updated_by'] = None if actor_id is None else int(actor_id)
        _atomic_write_json(self.path, current)
        return current

    def user_message(self) -> str:
        state = self.snapshot()
        reason = html.escape(str(state.get('reason') or 'Проводятся технические работы.'))
        return '🛠 <b>Технические работы</b>\n\n' + reason + '\n\nФункции бота временно недоступны. Попробуйте немного позже.'
