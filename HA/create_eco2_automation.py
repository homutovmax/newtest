import paramiko, json

HOST = '192.168.1.92'
USER = 'root'
PASS = 'CHANGE_ME'
TOKEN = 'CHANGE_ME'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=10)

# Read existing automations.yaml
stdin, stdout, stderr = ssh.exec_command('cat /DATA/AppData/homeassistant/config/automations.yaml', timeout=10)
existing = stdout.read().decode('utf-8', errors='replace')

# Check if our automation already exists
if 'mclh08_eco2_alert' in existing:
    print("Automation already exists, skipping creation")
else:
    automation_yaml = existing.rstrip() + "\n\n- id: mclh08_eco2_alert\n  alias: 'MCLH-08: Высокий eCO2 - вентиляция'\n  description: 'Оповещение при eCO2 > 600 ppm'\n  trigger:\n    - platform: numeric_state\n      entity_id: sensor.datchik_kachestva_vozdukha_eco2\n      above: 600\n  condition: []\n  action:\n    - service: tts.cloud_say\n      data:\n        entity_id: media_player.h96_94_2\n        message: 'Внимание! Уровень углекислого газа превышен. Нужно включить вентиляцию.'\n    - delay: '00:00:10'\n  mode: single\n"

    with ssh.open_sftp() as sftp:
        with sftp.open('/DATA/AppData/homeassistant/config/automations.yaml', 'w') as f:
            f.write(automation_yaml)

    print("Automation written to automations.yaml")

# Now call HA API to reload automations
import base64
reload_payload = base64.b64encode(json.dumps({}).encode()).decode()

cmd = f'curl -s -X POST -H "Authorization: Bearer {TOKEN}" -H "Content-Type: application/json" http://localhost:8123/api/services/automation/reload'
stdin, stdout, stderr = ssh.exec_command(cmd, timeout=15)
reload_out = stdout.read().decode('utf-8', errors='replace').strip()
reload_err = stderr.read().decode('utf-8', errors='replace').strip()
if reload_out:
    print(f"Reload: {reload_out}")
if reload_err:
    print(f"Reload error: {reload_err}")

# Verify
stdin, stdout, stderr = ssh.exec_command('cat /DATA/AppData/homeassistant/config/automations.yaml', timeout=10)
final = stdout.read().decode('utf-8', errors='replace')
if 'mclh08_eco2_alert' in final:
    print("\n=== Automation verified ===")
    lines = final.split('\n')
    start = next((i for i, l in enumerate(lines) if 'mclh08_eco2_alert' in l), None)
    if start is not None:
        for line in lines[start:start+20]:
            print(f"  {line}")
else:
    print("ERROR: Automation not found in file!")

ssh.close()
