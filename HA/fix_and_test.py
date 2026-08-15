import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)
sftp = ssh.open_sftp()

new_automations = """- id: '1775473559145'
  alias: 'Новая автоматизация'
  description: ''
  triggers:
  - domain: mqtt
    device_id: 0196fc11def14414d1123c23ffb7a4d5
    type: action
    subtype: single
    trigger: device
  conditions: []
  actions:
  - device_id: 2b94e62abad417dcb7e78ebd6c69fcf7
    domain: mobile_app
    type: notify
    message: 'Тест'
  mode: single
- id: '1779888932997'
  alias: 'Полив'
  description: ''
  triggers:
  - trigger: time
    at: '19:00:00'
    weekday:
    - mon
    - tue
    - wed
    - thu
    - fri
    - sat
    - sun
  conditions: []
  actions:
  - alias: 'Включить помпу'
    action: switch.turn_on
    metadata: {}
    target:
      device_id: e62af06f25687c668a6188e69fd40f2b
    data: {}
  - delay:
      hours: 0
      minutes: 10
      seconds: 0
      milliseconds: 0
  - action: switch.turn_off
    metadata: {}
    target:
      device_id: e62af06f25687c668a6188e69fd40f2b
    data: {}
  - action: switch.turn_on
    metadata: {}
    target:
      device_id: 4f3eb9b1a23ee62935310299b84d4055
    data: {}
  - delay:
      hours: 0
      minutes: 10
      seconds: 0
      milliseconds: 0
  - action: switch.turn_off
    metadata: {}
    target:
      device_id: 4f3eb9b1a23ee62935310299b84d4055
    data: {}
  mode: single
- id: '1782224949388'
  alias: 'CO2'
  description: 'Проверка датчика'
  triggers:
  - type: volatile_organic_compounds_parts
    device_id: de301810c08e46a9d0cdade29105b46b
    entity_id: a58685a78a449ded52e01d943f6cef34
    domain: sensor
    trigger: device
    above: 1000
  conditions: []
  actions:
  - action: notify.notify
    metadata: {}
    data:
      message: 'Проверка датчика! VOC-измерение включено!'
      title: 'Проверка датчика'
  mode: single
- id: mclh08_eco2_alert
  alias: 'MCLH-08: Высокий eCO2 - Вентиляция'
  description: 'Оповещение при eCO2 > 600 ppm через Яндекс Станцию Миди'
  trigger:
    - platform: numeric_state
      entity_id: sensor.datchik_kachestva_vozdukha_eco2
      above: 600
  condition: []
  action:
    - service: media_player.play_media
      target:
        entity_id: media_player.yandex_station_r1099440084h0y
      data:
        media_content_id: 'Внимание! Уровень углекислого газа повышен. Рекомендуется включить вентиляцию.'
        media_content_type: text
    - delay: '00:00:15'
  mode: single
"""

with sftp.open('/DATA/AppData/homeassistant/config/automations.yaml', 'w') as f:
    f.write(new_automations.encode('utf-8'))

print("Автоматизация обновлена: media_player.yandex_station_r1099440084h0y (Яндекс Станция Миди)")

# Reload automations
import urllib.request, json
TOKEN = 'CHANGE_ME'
req = urllib.request.Request("http://192.168.1.92:8123/api/services/automation/reload",
    data=b'{}',
    headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
    method="POST")
try:
    urllib.request.urlopen(req, timeout=30)
    print("Автоматизации перезагружены")
except:
    print("Reload отправлен")

# Test TTS on Mиди
import time
time.sleep(3)
req2 = urllib.request.Request("http://192.168.1.92:8123/api/services/media_player/play_media",
    data=json.dumps({
        "entity_id": "media_player.yandex_station_r1099440084h0y",
        "media_content_id": "Внимание! Уровень углекислого газа повышен. Рекомендуется включить вентиляцию.",
        "media_content_type": "text"
    }).encode(),
    headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
    method="POST")
try:
    urllib.request.urlopen(req2, timeout=30)
    print("TTS отправлено на Станцию Миди")
except Exception as e:
    print(f"Error: {e}")

sftp.close()
ssh.close()
