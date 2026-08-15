# Matter Server (python-matter-server)

## Развертывание на 192.168.1.92

### 1. Скопировать файлы на сервер

```bash
scp -r . user@192.168.1.92:/home/user/matter-server
```

### 2. Подключиться к серверу и запустить

```bash
ssh user@192.168.1.92
cd /home/user/matter-server
mkdir -p data
docker compose up -d
```

### 3. Проверить логи

```bash
docker compose logs -f
```

### 4. Подключение

Matter Server будет доступен по WebSocket:

```
ws://192.168.1.92:3000/ws
```

## Переменные окружения

- `TZ` — часовой пояс (по умолчанию Europe/Moscow)
- `CHIP_LOG_DETAIL` — детализация логов (1 = подробно)

## Режимы сети

- **bridge** (текущий) — порт 3000 проброшен на 5580. Работает, но mDNS может быть ограничен.
- **host** — если нужна полная поддержка mDNS для commissioning устройств, раскомментируй `network_mode: host` и убери `ports` и `networks`.

## Данные

Папка `data/` хранит:
- Matter Fabric credentials (сертификаты контроллера)
- Информацию о сопряженных устройствах
- Конфигурацию

При удалении `data/` создаётся новый Fabric — все устройства нужно будет перепривязывать.
