# HR — карьерная автоматизация

## Назначение

Автоматический пайплайн поиска вакансий для карьеры Максима Хомутова:
скрапинг hh.ru, Habr Career и rabota.sber.ru, классификация вакансий по 4 сценариям,
генерация отчёта, сопроводительных писем и резюме, рассылка в Telegram и на email.

## Стек

- **Python 3.10+**: FastAPI, SQLAlchemy 2, Alembic, Pydantic 2, Jinja2, requests
- **Веб:** PHP-шаблоны (`resume.php`, `resume_ai.php`, `send_to_telegram.php`)
- **БД:** PostgreSQL 16 (Docker)
- **Деплой:** Docker Compose (`hr-web-1`, `hr-db-1`), paramiko SFTP через Tailscale
- **ИИ:** DeepSeek API (генерация писем/резюме), Yandex SMTP (email)

## Две версии кода (важно!)

| Версия | Файлы | Запуск |
|--------|-------|--------|
| **Монолитная** | `update_vacancies.py` | локально: `python update_vacancies.py` |
| **Модульная** | `src/pipeline.py` + `src/scrapers/*` | на сервере в Docker (cron) |

Общая логика (`classify_title()`, `generate_letter()`) живёт в `generate_cover.py`
и импортируется обеими версиями. Фильтры `EXCLUDE_WORDS` синхронизируются вручную
в `update_vacancies.py` и `src/scrapers/shared.py`.

## Структура

```
HR/
├── update_vacancies.py         # монолит: скрапинг + отчёт + письма + Telegram
├── generate_cover.py           # ЕДИНЫЙ источник classify_title() + шаблоны писем
├── generate_cover_ai.py        # ИИ-генератор писем (DeepSeek)
├── generate_resume_ai.py       # ИИ-генератор резюме
├── deepseek_api.py             # клиент DeepSeek (urllib)
├── deepseek_config.json        # API-ключ — НЕ коммитится (шаблон: deepseek_config.example.json)
├── src/                        # модульная версия
│   ├── pipeline.py             # оркестратор (скрапинг → слияние → письма → отчёт → email)
│   ├── scrapers/shared.py      # фильтры + парсеры hh.ru/Habr
│   ├── scrapers/sber.py        # rabota.sber.ru
│   ├── scrapers/hh_ru.py, habr.py
│   ├── report.py               # генерация HTML-отчёта
│   ├── classify, cover, models, database, config, analytics, migration...
│   └── notifications/email.py  # рассылка по email
├── web/                        # FastAPI-приложение
│   ├── app.py                  # маршруты /report, /resume, /cover, /analytics, /history, /monitoring
│   ├── templates/*.html        # Jinja2-шаблоны
│   └── static/style.css
├── migrations/                 # Alembic (001–004)
├── tests/                      # регрессионные тесты
├── run_tests.py                # локальный запуск тестов
├── functional_test.py          # интеграционный тест на сервере (SSH)
├── ansible/deploy.yml          # playbook деплоя
├── docker-compose.yml          # web (FastAPI) + db (Postgres 16)
├── Dockerfile
├── deploy.sh, run_pipeline.sh, send_report.sh
├── resume.php, resume_ai.php   # PHP-страницы резюме
├── vacancies_report.html       # главный отчёт (табы по сценариям)
├── vacancies_history.json/html # история вакансий
├── archive/                    # ~100 одноразовых/диагностических скриптов (не активны)
├── AGENTS.md                   # полный контекст проекта для ИИ-агентов
└── .env.example                # шаблон переменных окружения
```

## Классификация вакансий

`classify_title()` в `generate_cover.py` — единственный источник правды.
4 сценария + `unknown`:

1. **telecom** — руководитель направления в телекоме/ИТ (CX, delivery, CTO…)
2. **ai_product** — Head of AI / директор по продукту
3. **strategy** — цифровая трансформация, efficiency, change
4. **ba** — руководитель бизнес-анализа (BPMN, UML, Camunda)

Ключевые слова и весовые баллы — в `AGENTS.md` (раздел «classify_title()»).

## Источники вакансий

- **hh.ru** — 4 широких запроса × 2 режима × 5 страниц (~40 запросов), парсинг HTML
  с учётом анти-бот защиты. Заглушка зарплаты «100 ₽» вырезается при парсинге.
- **Habr Career** — 18 запросов по сценариям.
- **rabota.sber.ru** — один API с пагинацией (`GET /public/.../publications?skip&take`).

## Команды

```bash
cd HR
python run_tests.py            # регрессионные тесты (exit 0 = готово к деплою)
python update_vacancies.py     # монолит: скрапинг + отчёт + письма (~3–4 мин)
docker compose up -d           # FastAPI web + PostgreSQL
docker compose logs -f         # логи контейнеров
```

## Деплой (чек-лист)

Подробный чек-лист — в `AGENTS.md` (раздел «Deployment Checklist»). Кратко:

1. `python run_tests.py` → exit 0
2. Локально `python update_vacancies.py`, проверить отчёт (табы, нет «100 ₽»)
3. Загрузить на сервер `192.168.1.92` (Tailscale `100.112.4.123`) через paramiko:
   `vacancies_report.html`, `vacancies_history.json`, `vacancies_history.html`,
   `update_vacancies.py`, `generate_cover.py` (+ `src/scrapers/shared.py` при изменении фильтров)
4. `docker restart hr-web-1`
5. Проверить http://192.168.1.92:8000/report

> ⚠️ Telegram bot token в `update_vacancies.py` и скриптах `archive/` заменён на `CHANGE_ME`.
> Перед локальным запуском монолита верните реальный токен.

## Тесты

`python run_tests.py` запускает все тесты в `tests/` (без сети/БД):

- `test_classify.py` — `classify_title()` + `generate_letter()`
- `test_filters.py` — `EXCLUDE_WORDS`, SBER-фильтры, `is_moscow_spb`
- `test_salary.py` — вырезание фиктивной зарплаты, `parse_salary_min`
- `test_cover.py` — корректность HTML письма
