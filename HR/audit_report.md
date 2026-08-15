# HR Project Audit Report

**Дата:** 2026-06-26
**Объём:** ~1033 vacancies, 14 FastAPI endpoints, Docker Compose, PostgreSQL 16

---

## Часть 1: Security Audit (FastAPI Security Best Practices)

### CRITICAL

| ID | Rule | Location | Issue |
|----|------|----------|-------|
| **SEC-001** | FASTAPI-OPENAPI-001 | `web/app.py:16` | OpenAPI docs (`/docs`, `/redoc`, `/openapi.json`) публично доступны через Tailscale Funnel. Информация о всех эндпоинтах доступна из интернета. |

**Impact:** Любой может узнать полную структуру API — типы данных, query-параметры, схемы ответов. Увеличивает поверхность атаки.

**Fix:** `app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)` в production. Или защитить auth-прокси.

---

### HIGH

| ID | Rule | Location | Issue |
|----|------|----------|-------|
| **SEC-002** | FASTAPI-XSS-001 | `web/app.py:116` + `web/templates/cover.html:12` | `cover_text` генерируется из `title` (приходит с hh.ru/Habr — untrusted), проходит через `re.sub(r'\*\*(.+?)\*\*', ...)` и рендерится с `{{ cover_text|safe }}`. Если title содержит `**<script>alert(1)</script>**`, регекс преобразует в `<strong><script>alert(1)</script></strong>` и `|safe` не эскейпит — XSS. |

**Impact:** Злоумышленник может разместить вакансию с вредоносным title → при открытии cover-письма выполняется JS в контексте домена.

**Fix:** Экранировать title при вставке в `generate_letter()`, либо не использовать `|safe` — вместо `|safe` конвертировать форматирование на стороне шаблона через `{{ cover_text }}` (Jinja2 autoescape).

| ID | Rule | Location | Issue |
|----|------|----------|-------|
| **SEC-003** | FASTAPI-HEADERS-001 | `web/app.py` — весь файл | Отсутствуют security-заголовки: `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy`. Приложение отдаёт HTML через Tailscale Funnel (публичный доступ). |

**Impact:** Возможен clickjacking, MIME-type sniffing, утечка referrer.

**Fix:** Добавить Starlette middleware для установки заголовков.

| ID | Rule | Location | Issue |
|----|------|----------|-------|
| **SEC-004** | FASTAPI-HOST-001 | `web/app.py` — весь файл | Не используется `TrustedHostMiddleware`. Приложение доступно через Tailscale Funnel, `Host`-заголовок не валидируется. |

**Impact:** Host header injection при генерации redirect-URL и в логах. В текущей версии — низкий риск (нет password-reset и т.п.), но база для будущих уязвимостей.

**Fix:** Добавить `TrustedHostMiddleware(allowed_hosts=["ibox-z3-2.taila7bc1e.ts.net", "192.168.1.92"])`.

| ID | Rule | Location | Issue |
|----|------|----------|-------|
| **SEC-005** | FASTAPI-PROXY-001 | `docker-compose.yml:34-35` | Uvicorn запущен без `--proxy-headers` и `--forwarded-allow-ips`. При этом приложение за Tailscale Funnel (reverse proxy). Без proxy headers `request.client.host` показывает IP Uvicorn-контейнера, а не клиента. `request.url.scheme` может быть `http` вместо `https`. |

**Impact:** Неверное определение схемы (http vs https), IP клиента. Условный риск (зависит от использования этих данных).

**Fix:** `uvicorn web.app:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips="*"` (с учётом что Funnel контролирует заголовки)

---

### MEDIUM

| ID | Rule | Location | Issue |
|----|------|----------|-------|
| **SEC-006** | FASTAPI-RESP-001 | `web/app.py:46-71`, `web/app.py:130-181` | Все эндпоинты возвращают ORM-объекты (`Vacancy`) напрямую в шаблоны без response-моделей. Хотя в JSON-эндпоинтах нет утечки (только `health`), все поля модели (включая `cover_text`, `status`) доступны в шаблонах — не проблема для текущего случая, но нет разделения на internal/external. |
| **SEC-007** | FASTAPI-LIMITS-001 | `web/app.py` — весь файл | Отсутствуют лимиты на размер запроса. Нет `max_request_size` middleware. В текущей реализации — низкий риск (нет file upload, read-only API), но потенциальный DoS-вектор. |
| **SEC-008** | Credential hygiene | `src/config.py:6` | `DB_URL` содержит пароль в default-значении (`hr:hr@localhost`). Если опоздать с установкой `.env`, приложение подключится к несуществующему localhost с дефолтными кредами. |
| **SEC-009** | Credential hygiene | `docker-compose.yml:23` | DB_URL передан с паролем `hr` напрямую (hardcoded), а не через `${DB_PASSWORD}`. Безопаснее использовать переменную. |

---

### LOW

| ID | Rule | Location | Issue |
|----|------|----------|-------|
| **SEC-010** | FASTAPI-SUPPLY-001 | `requirements.txt` | Зависимости имеют только нижние границы версий. Рекомендуется зафиксировать конкретные версии (`fastapi==0.115.6`). |
| **SEC-011** | Docker networking | `docker-compose.yml:15` | Порт PostgreSQL 5432 проброшен на хост. База доступна снаружи Docker (с паролем `hr`). Для работы достаточно внутренней сети. |
| **SEC-012** | .env.example | `.env.example` | Файл содержит только заглушки. `SMTP_PASSWORD` нет в примере — новый разработчик не узнает о необходимой переменной. |

---

## Часть 2: Architectural Audit

### 2.1 Codebase Hygiene — Проблема

```
C:\NEWTEST\HR\
├── check_*.py           # 20+ диагностических скриптов
├── deploy_*.py          # 10+ скриптов деплоя
├── fix_*.py             # 6 скриптов исправлений
├── ts_*.py              # 15+ скриптов Tailscale
├── __*.py               # 11 временных тестов
```

**~60 одноразовых/диагностических скриптов в корне.** Это legacy от итеративного процесса настройки. Они не нужны для работы приложения и создают шум.

**Fix:** Переместить в `archive/` или удалить. Актуальны только: `update_vacancies.py`, `generate_cover.py`, `deepseek_api.py`, `deepseek_config.json`.

### 2.2 Dual Code Path — Проблема

- **Standalone path:** `update_vacancies.py` — скрапит, генерирует отчёты, cover-письма напрямую (живёт в корне)
- **Docker path:** `src/pipeline.py` вызывает `update_vacancies.py` функции, `src/migration.py` переносит в PG

`src/pipeline.py:5` — `from update_vacancies import log` — импорт из корневого скрипта.
`src/analytics.py:4` — `from generate_cover import classify_title` — импорт из корневого скрипта.
`src/report.py:5-11` — импорт из `update_vacancies`.

Также в `src/scrapers/hh_ru.py:4-12` — импорт из `update_vacancies`.

Это **хрупкая архитектура**: `update_vacancies.py` ≈ 500+ строк монолитного скрипта, от которого зависят 5 модулей в `src/`.

**Impact:** Любое изменение в `update_vacancies.py` может сломать `src.pipeline`, `src.report`, `src.scrapers.*`, `src.analytics`.

**Fix:** Вынести общие функции (fetch, HH_QUERIES, parse, classify) в `src/scrapers/shared.py` и `src/classifier.py` (уже частично сделан). Убрать импорты из корневых скриптов.

### 2.3 Отсутствие тестов

`tests/__init__.py` — пустой. Нет ни unit, ни integration тестов. Критически важная логика (`classify_title()`, `generate_letter()`, `parse_hh_from_search()`) не покрыта.

**Fix:** Добавить тесты для `classify_title()` (дымовые тесты уже есть в `src/analytics.py:47-61` как runtime-проверка, но не как юнит-тест).

### 2.4 Отсутствие типов

Ключевые функции без аннотаций:
- `generate_letter(title, company, ...)` — `generate_cover.py:251` — нет return type
- `classify_title(title)` — `generate_cover.py:18` — нет return type
- `parse_hh_from_search(html)` — в `update_vacancies.py` — нет return type

### 2.5 Hardcoded paths

- `src/analytics.py:6-7` — `HISTORY_PATH = "vacancies_history.json"` — должен браться из config
- `src/send_report.py:18` — `http://192.168.1.92:8000/report` — URL захардкожен, не из `.env`
- `run_pipeline.sh:8-13` — имя контейнера `hr-web-1` захардкожено

---

## Часть 3: Operational Audit

| ID | Issue | Severity | Recommendation |
|----|-------|----------|----------------|
| OPS-001 | `run_pipeline.sh` запускает pipeline и migration как два отдельных `docker exec` | Medium | Объединить в один вызов или сделать `pipeline --with-migration` |
| OPS-002 | Нет log rotation для `/var/log/hr-pipeline.log` | Low | Добавить `logrotate` конфиг |
| OPS-003 | Нет docker-compose healthcheck для `web` сервиса | Low | Добавить `healthcheck` с `/health` эндпоинтом |
| OPS-004 | `src/analytics.py` читает HTML-файл отчёта, а не PG | Low | Либо читать из БД, либо убрать файловую зависимость |

---

## Part 4: Stress Test (The Fool) — Architecture Decisions

Применяю метод **Pre-mortem** (Gary Klein): представим, что прошло 6 месяцев и проект провалился. Почему?

### Failure 1: Server недоступен, а процесс ручной

Tailscale Funnel или сервер `192.168.1.92` упал. Деплой только через Ansible/SFTP на этот сервер. Нет fallback-инфраструктуры. Если сервер недоступен, pipeline не работает, email не отправляются.

**Вероятность:** Средняя (один сервер, нет HA)
**Mitigation:** Документировать ручной запуск локально (`python update_vacancies.py`) как fallback

### Failure 2: Устаревание классификации

`classify_title()` содержит ~80 хардкодных ключевых слов. Рынок вакансий меняется — новые роли (AI Agent Engineer, Prompt Architect, etc.) не попадают в категории. Через 6 месяцев качество классификации деградирует.

**Вероятность:** Высокая
**Mitigation:** Добавить ежемесячный аудит unknown-вакансий + автоматический анализ топ-слов в unknown

### Failure 3: Критическое изменение API hh.ru/Habr

Оба источника не имеют официального API для этого сценария (hh.ru — HTML-скрапинг, борьба с антиботом). Любое изменение HTML-структуры ломает парсер. Сейчас нет алерта при падении — ошибки тонут в `LOG=/var/log/hr-pipeline.log`.

**Вероятность:** Высокая
**Mitigation:** Добавить Telegram/email-алерт при ошибке скрапинга. Cегодня это было, но заблокировано `api.telegram.org`.

### Failure 4: Отсутствие мониторинга pipeline

Pipeline запускается по cron. Нет метрик: сколько длится, сколько вакансий найдено, успешно ли отправился email. Нет dashboard. Единственная обратная связь — email (который может не прийти при ошибке).

**Вероятность:** Высокая
**Mitigation:** Добавить `/health` с метриками последнего pipeline, время последнего успешного запуска, количество вакансий.

---

## Summary — Priority Actions

| Priority | ID | Effort | Impact |
|----------|----|--------|--------|
| P0 | SEC-002 | 1 час | XSS через cover-письма — **исправить немедленно** |
| P0 | SEC-001 | 5 мин | Выключить `/docs` в production |
| P1 | SEC-003 | 15 мин | Добавить security-заголовки |
| P1 | ARCH-1 | 1 час | Почистить корень от 60 мусорных скриптов |
| P2 | SEC-005 | 5 мин | Включить proxy-headers в Uvicorn |
| P2 | SEC-011 | 5 мин | Убрать `ports: [5432:5432]` из docker-compose |
| P2 | OPS-001 | 15 мин | Объединить pipeline+migration в один шаг |
| P3 | TESTS | 2 часа | Написать тесты для classify_title + generate_letter |
| P3 | MONITOR | 1 час | Добавить метрики pipeline в /health |
