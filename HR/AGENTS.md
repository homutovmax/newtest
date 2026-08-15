# HR Project — Maxim Khomutov Career Consulting

## Profile
- **Name:** Хомутов Максим Владимирович
- **Age:** 46
- **Location:** Королёв (Московская обл.), не готов к переезду, готов к командировкам
- **Email:** homutov.m@gmail.com
- **Phone:** +7 (916) 192-88-47 / +7 (916) 4573969
- **Experience:** 24 years in IT / Telecom
- **Salary target:** 780K – 1.2M RUB/month (70% fixed, 30% bonus) — **never show in letters or resume**

## Target Companies
Альфа-Банк, Сбер, Tele2, Ростелеком, СИБУР, Еврохим, БКС, ASTERUS, Норникель, Х5, Ivi

## Career History
| Period | Company | Role |
|--------|---------|------|
| 2024–2026 | МТС | Руководитель направления трайба «Клиентский сервис» |
| 2023–2024 | МТС | Руководитель направления технологической стратегии кластера CX |
| 2021–2023 | МТС | Руководитель ИТ-продукта «Мониторинг тендерной деятельности» |
| 2020–2021 | Ростелеком | Руководитель направления (оптимизация кабельных столов, BPMN) |
| 2018–2020 | СИБУР | Главный эксперт / руководитель группы бизнес-анализа |
| 2013–2018 | МГТС | Начальник отдела взаимодействия с бизнес-заказчиками |
| 2011–2012 | МТС | Бизнес-аналитик (Корпоративный центр, Siebel CRM) |

## Key Projects
- **GenAI-суфлер (голос):** пилот с ИБ-контуром, метрики, методика оценки
- **NLP орфография + Tone of Voice:** запущен в продуктив в чате
- **Платформа роботизации КЦ:** унификация API, снижение зависимости от вендора
- **R&D-конвейер:** 100+ AI-гипотез в неделю, приоритизация, передача в продукты
- **Технологическая стратегия CX:** техзрелость с низкой до 4/5 за 1.5 года
- **БА в СИБУРе:** создание подразделения с нуля (6+5 удалённых), методология, change management
- **Мониторинг тендерной деятельности:** рост выигранных тендеров на 45%
- **Оптимизация кабельных столов Ростелекома:** BPMN (Camunda), сокращение численности
- **Data Governance:** внедрение в продуктах CX

## Resume Scenarios
| # | Name | Auto-detect | Target Roles |
|---|------|-------------|--------------|
| 1 | Telecom / IT — Руководитель направления | телеком, telecom, связь, инфраструктур, cto, devops, delivery, client, сервис, cx, руководител, направлени, платформ | Head of CX, Delivery Manager, Руководитель ИТ-продукта |
| 2 | Head of AI / Product — Директор по продукту | ai, ии, artificial, ml, data, product, head, cpo | Head of AI, Director of AI Products, R&D Lead |
| 3 | Strategic / Transformation | стратег, трансформаци, digital+transform, эффективност, change, инноваци | Директор по трансформации, Head of Process Excellence |
| 4 | Business Analysis — Руководитель БА | бизнес-анали, bpmn, uml, требований, camunda, epc, процесс, автоматизаци | Lead BA, Head of BA, Business Process Manager |

## Cover Letter Categories (generate_cover.py)
Same 4 categories as resume. `classify_title()` uses keyword scoring:
- BA wins if ba_score=4 > max of others (telecom +2, ai_product +3/+2, strategy +5/+3/+1)

## Infrastructure
- **Сервер:** 192.168.1.92 (Tailscale 100.112.4.123, root/CHANGE_ME)
- **Docker:** `hr-web-1` (порт 8000, FastAPI + uvicorn) + `hr-db-1` (PostgreSQL 16)
- **Web:** http://192.168.1.92:8000 | Tailscale: https://ibox-z3-2.taila7bc1e.ts.net
- **Cron:** run_pipeline.sh (10:00 MSK) + send_report.sh (14:00 MSK) на сервере
- **Email:** Yandex SMTP (maximumkh@yandex.ru → homutov.m@gmail.com) через Docker
- **Python:** 3.10 (с requests, paramiko) внутри контейнера
- **Деплой:** paramiko SFTP через Tailscale в `/opt/hr/`
- **Локальный запуск:** `python update_vacancies.py` (монолитная версия)

## Versions (WARNING: code fork)
- **Монолитная** — `C:\NEWTEST\HR\update_vacancies.py` (локальный запуск, hh.ru + Habr + employer search + Сбер + порталы)
- **Модульная** — `src/pipeline.py` → `src/scrapers/(shared|hh_ru|habr).py` (на сервере в Docker, только hh.ru + Habr)
- `classify_title()` и `generate_cover()` общие — в `generate_cover.py` (импортируется обоими версиями)
- Фильтры (EXCLUDE_WORDS, is_habr_relevant) синхронизированы вручную

## Critical Constraints
1. **hh.ru applicant API closed** → HTML scraping with anti-bot countermeasures
2. **Dummy "100 ₽" from hh.ru** → stripped at parse time via `re.sub(r'[\s\u00a0\u20bd\u0440\u0443\u0431\.]', '', s)` check for `''`, `'100'`, `'0'`, `'–'`. Also applied for руб. variants. All downstream uses (report, email, history, covers) see empty salary.
3. **Status "new" sticky within same day** — в history.update: если `firstSeen == today`, статус остаётся `new`, не сбрасывается в `active`. Иначе дашборд показывает 0 новых при повторном запуске в тот же день.
4. **Habr key double-prefix** (FIXED 2026-06-25): reading from list-format history prepended another `habr-` to `item["id"]` which already had `habr-` prefix → 78 garbage keys. Fixed by checking source before prepending.
5. **Cover HTML escaping** (FIXED 2026-06-25): `_cover_html()` now uses `html.escape()` on all title/company/salary/location/category, converts `**bold**` → `<strong>bold</strong>` and `\n` → `<br>`.
6. **Filter sync** (ADDED 2026-06-28): монолитная и модульная версии имеют раздельные EXCLUDE_WORDS + filter logic. Синхронизация делается вручную — править нужно оба файла: `update_vacancies.py` + `src/scrapers/shared.py` на сервере.
7. **Tailscale required for deploy** — сервер 192.168.1.92 доступен через Tailscale (100.112.4.123). SSH от локальной машины не работает (висит), только paramiko через Tailscale.

## Key Commands
- Локальный запуск: `cd C:\NEWTEST\HR && python update_vacancies.py`
- Деплой на сервер: запустить скрипт `deploy_to_server.py` (через paramiko SFTP)
- Restart контейнера: `docker restart hr-web-1` на сервере
- Report URL: http://192.168.1.92:8000/report

## File Map (active files only)
| File | Purpose |
|------|---------|
| `update_vacancies.py` | Main scraper + report generator + cover generator (cron: hr_bot/). Searches 4 broad hh.ru + 18 Habr queries + 1 rabota.sber.ru API across all 4 profiles. Sorts: new today first, then salary. Report has tabs by scenario (All/Telecom/AI/Strategy/BA/Other). Telegram sends only new today vacancies. Cover letters generated via direct function call (no subprocess). |
| `generate_cover.py` | **Single source of truth for `classify_title()`**. Template-based cover letters (4 categories, deterministic by seed). Exports `generate_letter()` called directly by `update_vacancies.py`. Also has CLI: `python3 generate_cover.py classify <title_b64>` returns `{"scenario": 1..4}`. |
| `generate_cover_ai.py` | AI cover generator (fallback: returns error if API fails) |
| `generate_resume_ai.py` | AI resume generator (called by resume_ai.php) |
| `deepseek_api.py` | DeepSeek API client (urllib, no external deps) |
| `deepseek_config.json` | API key storage |
| `resume.php` | Template resume page (4 scenarios). Classification via `generate_cover.py classify` subprocess (no PHP logic). |
| `resume_ai.php` | AI resume page (with loading + fallback to resume.php). Note: "Резюме" button in report now opens `resume.php` directly (AI returns 402). |
| `send_to_telegram.php` | Telegram delivery (calls Python via stdin pipe) |
| `tg_send.py` | Python helper for Telegram (reads from stdin) |
| `tg_bot.py` | Telegram bot polling script (cron: hr_bot/). Processes commands: /start, /help, /new (сегодняшние), /report (ссылка), /gen {title} // {company} (генерация письма) |
| `vacancies_report.html` | Main dashboard with ~296 vacancies, scenario tabs (hh.ru + Habr + Сбер + порталы) |
| `vacancies_history.*` | History tracking (JSON + HTML) |
| `cover_v*.html` | ~233 pre-generated static cover letters (template-based) |
| `src/scrapers/shared.py` | **Модульная версия** — фильтры (EXCLUDE_WORDS, is_habr_relevant), hh.ru + Habr парсеры |
| `src/pipeline.py` | **Модульная версия** — оркестратор (скрапинг → слияние → covers → отчёт → email) |
| `src/classifier.py` | Модульная версия — просто реэкспорт `classify_title()` из `generate_cover.py` |
| `AGENTS.md` | This file — project context for AI |
| `run_tests.py` | Local regression test runner (no network). Exit code 0 = deploy-ready |
| `tests/test_classify.py` | classify_title() + generate_letter() unit tests |
| `tests/test_filters.py` | EXCLUDE_WORDS, SBER_MGMT/SBER_REJECT, is_moscow_spb |
| `tests/test_salary.py` | Dummy salary stripping, esc(), parse_salary_min |
| `tests/test_cover.py` | _cover_html output — valid HTML, no raw code |

## Regression Tests (run before deploy)
`python run_tests.py` — runs all tests in `tests/`, exit code 0 = all pass.
Tests cover: classify_title, generate_letter, EXCLUDE_WORDS validation, SBER filters,
dummy salary stripping, HTML escaping, _cover_html formatting, is_moscow_spb logic.
Tests are LOCAL (no network/DB dependency), fast, and pure Python.
For full integration test on server: `python functional_test.py` (needs SSH access).

## Deployment Checklist (CRITICAL — must follow every time)
1. **Run regression tests**: `cd C:\NEWTEST\HR && python run_tests.py` — verify exit code 0
2. **Run locally**: `python update_vacancies.py` — generates `vacancies_report.html`, `vacancies_history.json`, `vacancies_history.html`
3. **Verify output**: check that report has tabs (`tab-btn` in HTML) and no dummy salaries (`100 ₽`)
4. **Upload files to server** via paramiko через Tailscale:
   - `vacancies_report.html` → `/opt/hr/vacancies_report.html`
   - `vacancies_history.json` → `/opt/hr/vacancies_history.json`
   - `vacancies_history.html` → `/opt/hr/vacancies_history.html`
   - `update_vacancies.py` → `/opt/hr/update_vacancies.py`
   - `generate_cover.py` → `/opt/hr/generate_cover.py`
   - Если менялись фильтры — также `src/scrapers/shared.py` → `/opt/hr/src/scrapers/shared.py`
5. **Restart container**: `docker restart hr-web-1`
6. **Verify**: open http://192.168.1.92:8000/report — check tabs work, no 100 ₽
7. **Performance**: hh.ru search ~30s, Habr ~20s, cover generation ~2.5min, total ~3-4min locally. На сервере через Docker ~3-5min.

## classify_title() — single source of truth in generate_cover.py
**`classify_title()` lives ONLY in `generate_cover.py`** (lines 16-53). `update_vacancies.py` imports it. 4 categories + `unknown`:
- **telecom**: +2 (руководител, devops, cto, связь, cx, телеком, инфраструктур, etc.) +1 (клиентский сервис, delivery)
- **ai_product**: +3 (artificial, ml, data science, cpo) +2 (ai, ии, data, данн, продукт, product, head)
- **strategy**: +5 (цифров+трансформаци together) +3 (strateg, стратег, efficiency, change, инноваци) +1 (digital or transform alone)
- **ba**: +4 (bpmn, uml, camunda, business analyst, etc.) +2 (требован, requirement, аналитик) +1 (процесс, process, automation)
- **unknown**: возвращается если все скоры = 0 (нет совпадений)
**hh.ru (4 broad queries × 2 modes × 5 pages = 40 requests):** Telecom/IT, AI/Product, Strategy, BA — each with OR-joined keywords. Each query runs as name-only + full-text search, 5 pages × 20 items = ~100 results per mode. Details parsed directly from search page HTML (no slow detail fetches). ~584 results deduped, classified by `classify_title()`.
**Habr Career (18 queries):** руководитель направления AI, Head of AI, CPO product AI, директор по продукту AI, цифровая трансформация, руководитель направления телеком, CTO AI, руководитель направления стратегия, директор по трансформации, Head of product AI, AI архитектор, технический директор AI, руководитель бизнес-анализа, Lead Business Analyst, бизнес-аналитик, BPMN аналитик, системный аналитик, управление требованиями
**rabota.sber.ru (Single API call with pagination):** `GET /public/app-candidate-public-api-gateway/api/v1/publications?skip={n}&take=50` — 3751 вакансий. Поля: title, company, salary_min/max, city, region, publicationDate, duties/requirements/conditions, internalId. Фильтр: Москва/СПб/удалёнка, исключение EXCLUDE_WORDS. Salary почти всегда null (генерики Сбера не показывают зарплату). URL: `https://rabota.sber.ru/search/{internalId}/`. ID: sber-{publicationId}.
