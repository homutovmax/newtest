# SWAP — Equipment Request Portal

## Назначение

Веб-портал для управления заявками на закупку оборудования. Заявки создают внешние
**Подрядчики (Contractors)**, внутренние **Кураторы (Curators)** распределяют их
между **Операторами (Operators)** и контролируют выполнение, а Операторы выполняют
работу: проверяют склад, заменяют позиции, экспортируют в Excel, импортируют в OEBS
и закрывают заявку.

Кнопки ручного «Approve» нет: после автоматической проверки (Review) система сразу
резервирует склад и переводит заявку в статус `RESERVED`.

## Стек

- **Frontend:** React 19, TypeScript, Vite 8, Ant Design 6, dayjs, uuid
- **Линтер:** oxlint (`.oxlintrc.json`)
- **Backend (по спецификации):** NestJS, PostgreSQL, Docker, Kubernetes
  — в репозитории реализован только frontend; API описан в спецификации.

## Структура

```
SWAP/
├── SWAP_Equipment Request Portal Blueprint.md   # полная спецификация (роли, статусы, API, модель данных)
└── frontend/
    ├── public/          # favicon.svg, icons.svg
    ├── src/
    │   ├── main.tsx     # точка входа
    │   ├── App.tsx      # Layout, роли, роутинг страниц
    │   ├── App.css, index.css
    │   ├── types/index.ts        # UserRole, RequestStatus, сущности, подписи статусов
    │   ├── store/mockData.ts     # мок-данные и «магазин» (без бэкенда)
    │   ├── pages/ContractorPage.tsx  # создание запроса, мои запросы
    │   ├── pages/CuratorPage.tsx     # панель куратора (все заявки, назначение)
    │   └── pages/OperatorPage.tsx    # очередь оператора, склад, экспорт/импорт
    ├── package.json, vite.config.ts, tsconfig*.json
    └── .oxlintrc.json
```

## Роли и рабочие пространства

| Роль | Возможности (UI) |
|------|------------------|
| **Contractor (Подрядчик)** | Создание запроса (организация, контакт, AOP-номер, таблица материалов), черновик/отправка, «Мои запросы», редактирование при `REVISION` |
| **Curator (Куратор)** | Все заявки, фильтры, назначение/переназначение оператора, мониторинг статусов, аудит-лог, SLA-уведомления |
| **Operator (Оператор)** | Открытие заявки (`IN_PROGRESS`), проверка склада (WMS), замена позиций, синхронизация с AOP, экспорт Excel, подтверждение импорта OEBS, закрытие |

## Поток статусов

```
DRAFT → SUBMITTED → REVIEW → (REVISION) OR (RESERVED) → ASSIGNED → IN_PROGRESS
→ STOCK_CHECK → (EDITED) → READY_FOR_EXPORT → EXPORT_DONE → IMPORT_PENDING
→ (IMPORTED) OR (IMPORT_ERROR) → (EDITED) OR (REVISION) → CLOSED
```

Полное описание статусов, прав, API-спецификации и модели данных PostgreSQL — в
файле [`SWAP_Equipment Request Portal Blueprint.md`](../SWAP/SWAP_Equipment%20Request%20Portal%20Blueprint.md).

## Команды

```bash
cd SWAP/frontend
npm install      # установка зависимостей
npm run dev      # dev-сервер Vite
npm run build    # production-сборка (tsc -b && vite build)
npm run lint     # oxlint
npm run preview  # предпросмотр собранного приложения
```

## Статус реализации

- Реализован **frontend-прототип** на мок-данных (`src/store/mockData.ts`):
  три роли переключаются в шапке, страницы под каждую роль.
- Backend, SSO/MFA, планировщик Review, WMS-адаптер, Excel-генератор,
  уведомления и аудит-лог — **по спецификации** (в репозитории не реализованы).
