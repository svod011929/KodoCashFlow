# Kodo v61 — Pterodactyl shared-hosting without Panel API

## Главная причина релиза

v61 делает Client API необязательным. Основной режим теперь полностью локальный и не требует URL панели, API key или административных прав.

## Живые ресурсы

- RAM usage/limit, swap, CPU quota/cpuset, PIDs, OOM и OOM-kill читаются прямо из cgroup v2/v1 текущего контейнера.
- Для cgroup v2 используется `cpu.stat usage_usec`, для v1 — `cpuacct.usage`.
- `P_SERVER_UUID`, `P_SERVER_LOCATION` и `SERVER_MEMORY` распознаются как Pterodactyl environment hints.
- Resource worker работает без рекурсивного scan диска в частом monitor loop.

## Диск

- Client API не обязателен для основного сценария.
- Лимит может задаваться явной startup variable / настройкой полного коммерческого билда.
- При отсутствии точного allocation интерфейс не подменяет его размером host filesystem.

## Runtime

- `APP_VERSION=61`.
- `architecture_version=61`.
- `storage_cleanup_version=61`.
- `pterodactyl_resource_sync_version=61`.
- `pterodactyl_runtime_optimization_version=61`.

> Полные migration, admin-flow и behavior-defining tests относятся к коммерческой сборке и не публикуются в showcase edition.
