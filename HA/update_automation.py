import paramiko

HOST = '192.168.1.92'
USER = 'root'
PASS = 'CHANGE_ME'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=10)
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
  description: 'Оповещение при eCO2 > 600 ppm через Яндекс колонку'
  trigger:
    - platform: numeric_state
      entity_id: sensor.datchik_kachestva_vozdukha_eco2
      above: 600
  condition: []
  action:
    - service: media_player.play_media
      target:
        entity_id: media_player.yandex_station_m10ns3600380kb
      data:
        media_content_id: 'Внимание! Уровень углекислого газа повышен. Рекомендуется включить вентиляцию.'
        media_content_type: text
    - delay: '00:00:15'
  mode: single
"""

with sftp.open('/DATA/AppData/homeassistant/config/automations.yaml', 'w') as f:
    f.write(new_automations.encode('utf-8'))

print("Automations updated successfully!")
print("Automation ID: mclh08_eco2_alert")
print("Speaker: media_player.yandex_station_m10ns3600380kb")
print("Text: Внимание! Уровень углекислого газа повышен. Рекомендуется включить вентиляцию.")

sftp.close()
ssh.close()
