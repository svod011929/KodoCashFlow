# Отчёт по локальной оптимизации Pterodactyl v61

## Итог

Для shared-hosting правильным источником фактически применённых ограничений RAM и CPU является Linux cgroup контейнера. Эти данные доступны процессу без доступа к Pterodactyl Panel.

Disk allocation устроен иначе: Pterodactyl/Wings учитывает размер server directory как application-level лимит, а не как стандартный cgroup resource. Поэтому процесс внутри контейнера не должен подменять disk allocation размером host filesystem.

## Подход runtime

1. Определение cgroup v1/v2 с учётом mount points.
2. `SERVER_MEMORY` используется только как fallback, если kernel limit недоступен.
3. Live CPU sampling строится по разнице cumulative cgroup usage.
4. Resource profile выбирается по фактически применённым RAM/CPU limits.
5. Частый resource loop не выполняет рекурсивное сканирование диска.

## Граница публичной версии

Полный Pterodactyl integration layer, Telegram admin flow, миграции и deployment behavior входят в коммерческую сборку **KodoCashFlow v61** и намеренно не публикуются.

**Полная рабочая версия: $20 через Telegram @KodoDrive.**
