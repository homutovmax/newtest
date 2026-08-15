# HA — диагностика и автоматизация Home Assistant

## Назначение

Набор Python-скриптов для диагностики, настройки и автоматизации умного дома на
Home Assistant, развёрнутого на сервере `192.168.1.92`. Скрипты выполняются
локально с этого ПК и работают с сервером по SSH/API.

## Состав

```
HA/
├── docker-compose.yml        # Matter Server (python-matter-server)
├── README.md                 # инструкция по развёртыванию Matter Server
├── .venv/                    # виртуальное окружение (не коммитится)
├── check_*.py                # диагностические проверки
├── fix_*.py                  # исправления конфигурации
├── setup_*.py                # настройка автоматизаций и интеграций
├── configure_ha_mqtt*.py     # настройка MQTT
├── pair_mclh08.py            # сопряжение датчика MCLH-08 (Matter)
├── calibrate_mclh.py         # калибровка датчика
├── monitor*.py               # мониторинг состояния
├── restart_ha.py, wait_ha.py # перезапуск/ожидание HA
└── *.txt, *.json             # результаты проверок и выгрузки
```

## Основные задачи (примеры скриптов)

| Задача | Скрипты |
|--------|---------|
| Проверка доступности HA и интеграций | `check_ha.py`, `check_ha_status.py`, `check_hacs.py`, `check_haier.py`, `check_z2m.py` |
| Проверка сети (DNS, VPN, Unifi) | `check_dns.py`, `check_vpn.py`, `check_unifi.py`, `check_unifi_devices.py`, `check_unifi_mongo.py` |
| Качество воздуха и калибровка датчиков | `check_airquality_extend.py`, `calibrate_mclh.py`, `check_voc_calibration.py`, `check_mclh_calibration.py` |
| Яндекс Станции и TTS | `check_yandex*.py`, `install_yandex*.py`, `setup_yandex_flow*.py`, `fix_tts.py` |
| Колонки и воспроизведение | `check_speakers.py`, `check_player.py`, `test_both_speakers.py` |
| Docker и диск | `check_docker_after_restart.py`, `check_disk_space.py`, `prune_docker.py`, `docker_cleanup.py`, `setup_auto_cleanup.py` |
| Автоматизации | `read_automations.py`, `reload_automation.py`, `create_eco2_automation.py`, `update_automation.py` |
| MQTT | `mqtt_pub*.py`, `send_mqtt.py`, `configure_ha_mqtt*.py` |
| Утилиты | `ssh_cmd.py`, `wait_ha.py`, `restart_ha.py`, `monitor.py`, `setup_monitor.py` |

## Matter Server

`docker-compose.yml` поднимает `ghcr.io/home-assistant-libs/python-matter-server`.

```bash
cd HA
docker compose up -d
```

- WebSocket: `ws://<host>:3000/ws` (проброс 3000 → 5580 в bridge-сети).
- Данные (сертификаты Fabric, сопряжённые устройства) хранятся в `data/` — при
  удалении папки создаётся новый Fabric, все устройства нужно перепривязывать.
- Если нужна полная поддержка mDNS для commissioning — переключить на
  `network_mode: host` (убрать `ports` и `networks`).

## Заметки

- Многие скрипты — одноразовые «диагностики» для конкретной проблемы; повторное
  использование требует чтения кода и адаптации адресов/параметров.
- Учётные данные (SSH-пароль `CHANGE_ME`, токен Home Assistant `CHANGE_ME`) вычищены
  из репозитория — перед запуском верните реальные значения в локальные копии скриптов.
