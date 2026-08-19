# Kodo v61 — Pterodactyl shared-hosting без Panel API

## Главная причина релиза

Версия v61 делает Client API необязательным. Основной режим теперь полностью локальный и не требует URL панели, API key или административных прав.

## Живые ресурсы

- использование и лимит RAM, swap, CPU quota/cpuset, PIDs, OOM и OOM-kill читаются прямо из cgroup v2/v1 текущего контейнера;
- для cgroup v2 используется `cpu.stat usage_usec`, для v1 — `cpuacct.usage`;
- `P_SERVER_UUID`, `P_SERVER_LOCATION` и `SERVER_MEMORY` распознаются как подсказки окружения Pterodactyl;
- worker мониторинга ресурсов работает без рекурсивного сканирования диска в частом цикле мониторинга.

## Диск

- Client API не обязателен для основного сценария;
- лимит может задаваться отдельной startup-переменной или настройкой полной коммерческой сборки;
- при отсутствии точного allocation интерфейс не подменяет его размером host filesystem.

## Runtime

- `APP_VERSION=61`;
- `architecture_version=61`;
- `storage_cleanup_version=61`;
- `pterodactyl_resource_sync_version=61`;
- `pterodactyl_runtime_optimization_version=61`.

> Полные миграции, admin-flow и behavior-defining tests относятся к коммерческой сборке и не публикуются в публичной витрине.

Полная рабочая версия **KodoCashFlow v61** доступна за **$20** через Telegram **@KodoDrive**.
