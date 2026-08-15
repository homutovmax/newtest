# newtest

Локальный репозиторий-«сборка» проектов, ведущихся на одном рабочем ПК.
Удалённый origin: `https://github.com/homutovmax/newtest.git` (ветка `master`).

## Состав репозитория

| Каталог | Проект | Назначение | Стек |
|---------|--------|------------|------|
| [`SWAP/`](SWAP/) | **SWAP — Equipment Request Portal** | Веб-портал заявок на оборудование (Подрядчики → Кураторы → Операторы) | React 19, TypeScript, Vite, Ant Design |
| [`HR/`](HR/) | **HR — карьерная автоматизация** | Скрапинг вакансий (hh.ru, Habr, Сбер), генерация отчётов, сопроводительных писем и резюме | Python, FastAPI, Docker, PostgreSQL, PHP |
| [`HA/`](HA/) | **HA — Home Assistant диагностика** | Набор скриптов для диагностики, настройки и автоматизации Home Assistant / Matter / MQTT | Python, Docker, Home Assistant |
| [`TESTPC/`](TESTPC/) | **Диагностика ПК** | Отчёт Windows Battery Report (saved HTML) | HTML |
| `snake.html`, `main.js`, `package.json` | **Snake Game (Electron)** | Мини-игра «Змейка» как тестовый Electron-проект | Electron |

Подробная документация по каждому подпроекту — в каталоге [`docs/`](docs/).

## Структура

```
newtest/
├── SWAP/                 # Equipment Request Portal (frontend)
│   ├── SWAP_Equipment Request Portal Blueprint.md   # спецификация портала
│   └── frontend/         # React + TS + Vite + Ant Design SPA
├── HR/                   # карьерная автоматизация (вакансии)
│   ├── update_vacancies.py        # монолит: скрапинг + отчёт + письма
│   ├── generate_cover.py          # классификатор вакансий + шаблоны писем
│   ├── src/                       # модульная версия пайплайна
│   ├── web/                       # FastAPI-приложение (отчёт, резюме, письма)
│   ├── tests/                     # регрессионные тесты
│   ├── migrations/                # Alembic-миграции PostgreSQL
│   ├── ansible/                   # playbook деплоя
│   ├── archive/                   # архив одноразовых/диагностических скриптов
│   └── AGENTS.md                  # контекст проекта для ИИ-агентов
├── HA/                   # скрипты диагностики Home Assistant
│   ├── check_*.py        # диагностические проверки
│   ├── fix_*.py          # исправления
│   ├── setup_*.py        # настройка автоматизаций
│   └── docker-compose.yml         # Matter Server
├── TESTPC/
│   └── battery-report.html        # отчёт о состоянии батареи ПК
├── docs/                 # документация этого репозитория
│   ├── README.md
│   ├── SWAP.md
│   ├── HR.md
│   └── HA.md
├── snake.html            # игра «Змейка»
├── main.js               # Electron-обёртка для snake.html
├── package.json          # зависимости Electron
├── .gitignore
└── README.md
```

## Быстрый старт

### SWAP — frontend

```bash
cd SWAP/frontend
npm install
npm run dev        # режим разработки (Vite)
npm run build      # production-сборка
npm run lint       # oxlint
```

### HR — пайплайн вакансий

```bash
cd HR
python run_tests.py          # регрессионные тесты (без сети)
python update_vacancies.py   # монолитная версия: скрапинг + отчёт + письма
docker compose up -d         # поднять web (FastAPI) + db (PostgreSQL 16)
```

### HA — Matter Server

```bash
cd HA
docker compose up -d
# WebSocket: ws://<host>:3000/ws
```

## Безопасность

**Секреты из репозитория вычищены** и заменены плейсхолдером `CHANGE_ME`. При работе со скриптами
необходимо вручную вернуть реальные значения (SSH-пароль сервера, токен Home Assistant, SMTP-пароль,
Telegram bot token) в локальные копии файлов.

Следующие файлы **не** коммитятся (исключены через `.gitignore`) и должны создаваться локально:

- `HR/deepseek_config.json` — API-ключ DeepSeek (см. шаблон `HR/deepseek_config.example.json`)
- `HR/maximum64.txt` — локальные учётные данные
- `.env` — переменные окружения (шаблон: `HR/.env.example`)

> ⚠️ В `HR/AGENTS.md` и скриптах `HA/`, `HR/` находятся адреса внутренней инфраструктуры
> (сервер `192.168.1.92`, Tailscale). При публикации в открытый доступ их также следует удалить.

## Соглашения

- Ветка по умолчанию: `master`.
- Рабочий процесс: локальная разработка → коммит → деплой скриптами (`HR/deploy.sh`, paramiko SFTP через Tailscale).
- Для HR перед деплоем обязателен запуск `python run_tests.py` (exit code 0).
