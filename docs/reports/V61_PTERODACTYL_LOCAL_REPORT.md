# V61 Pterodactyl local optimization report

## Итог

Для shared-hosting сценария правильным источником фактически применённых RAM и CPU ограничений является Linux cgroup контейнера. Эти данные доступны процессу без доступа к Pterodactyl Panel.

Disk allocation отличается: Pterodactyl/Wings учитывает объём server directory как application-level лимит, а не как стандартный cgroup resource. Поэтому процесс внутри контейнера не должен подменять disk allocation размером host filesystem.

## Runtime approach

1. Mount-aware cgroup v1/v2 discovery.
2. `SERVER_MEMORY` используется только как fallback, если kernel limit не читается.
3. Live CPU sampling строится по delta cumulative cgroup usage.
4. Resource profile подбирается по фактически применённым RAM/CPU limits.
5. Частый resource loop не делает рекурсивный disk scan.

## Showcase boundary

Полный Pterodactyl integration layer, Telegram admin flow, migrations и deployment behavior входят в коммерческую сборку KodoCashFlow v61.

**Full runnable version: $20 via Telegram @KodoDrive.**
