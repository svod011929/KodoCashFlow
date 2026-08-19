<div align="center">

# 💸 KodoCashFlow v61

### Telegram automation platform · Pterodactyl-ready · SQLite-first

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
![Version](https://img.shields.io/badge/version-v61-7c3aed)
![Edition](https://img.shields.io/badge/edition-showcase-f59e0b)
![Pterodactyl](https://img.shields.io/badge/Pterodactyl-local%20monitoring-0ea5e9)
[![Telegram](https://img.shields.io/badge/Buy%20full%20version-%40KodoDrive-26A5E4?logo=telegram&logoColor=white)](https://t.me/KodoDrive)

**Public showcase edition. The runnable commercial core is intentionally not published.**

### 💵 Full runnable version — **$20**
### 📩 Purchase / support: **[@KodoDrive](https://t.me/KodoDrive)**

</div>

---

## What is KodoCashFlow?

KodoCashFlow is a production-oriented Telegram automation platform built for long-running deployment inside **Pterodactyl containers**. Version 61 focuses on local resource visibility without requiring the Pterodactyl Client API, durable SQLite storage, safe cleanup, modular providers, background workers, notifications and operational tooling.

This repository is intentionally a **showcase / architecture edition**. It demonstrates the project structure and a meaningful part of the infrastructure while keeping the commercial implementation private.

> [!IMPORTANT]
> This repository **cannot be started as a complete bot**. The canonical launcher and proprietary core modules are deliberately excluded. The complete runnable package is available from **@KodoDrive for $20**.

## ✨ Highlights of the full version

- 🤖 Telegram bot architecture based on `aiogram`
- 🧩 Modular handlers, repositories and provider registry
- 💾 SQLite-first persistence with WAL-aware maintenance
- 🧹 Automated storage cleanup and retention policies
- 🦅 Local Pterodactyl resource monitoring through cgroup v1/v2
- 📊 Runtime profiles tuned for low / balanced / high-resource containers
- 🔔 Durable notification and background-task infrastructure
- 💰 Financial helpers, payout workflows and operational safeguards
- 🔐 Secret storage separated from the database
- 🌐 HTTP runtime and external integration layer
- 🔄 Versioned database migrations and backward-compatibility tooling

## 🦅 Pterodactyl v61

The v61 runtime can read container limits locally instead of depending on panel API credentials. Depending on the host, it can inspect RAM and swap usage, CPU quota / cpuset information, PID limits, OOM counters, cumulative CPU usage and project disk usage.

## 📦 Public showcase

This repository contains selected architecture, configuration, infrastructure and technical documentation. It intentionally omits the canonical launcher, central application core, legacy compatibility logic, sensitive payout/access workflows, provider implementations and behavior-defining test suite.

The repository is therefore a technical showcase, **not a free runnable distribution**.

## 🛒 Get the full version

The complete build includes the missing commercial files, real launch path, provider implementations, compatibility logic, tests and full deployment configuration.

<div align="center">

### **Price: $20**
### Telegram: **[@KodoDrive](https://t.me/KodoDrive)**

When contacting me, mention **KodoCashFlow v61**.

</div>

## 🧱 Technology

- Python 3.10+
- aiogram
- aiohttp
- aiosqlite / SQLite
- Pterodactyl-compatible Linux containers

## 👤 Author

**KodoDrive**  
GitHub: **[@svod011929](https://github.com/svod011929)**  
Telegram: **[@KodoDrive](https://t.me/KodoDrive)**

---

<div align="center">

**KodoCashFlow v61 · Showcase Edition**  
Full runnable package: **$20 via @KodoDrive**

</div>
