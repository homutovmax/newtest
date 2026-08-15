import paramiko, json

HOST = '192.168.1.92'
USER = 'root'
PASS = 'CHANGE_ME'
TOKEN = 'CHANGE_ME'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=10)

script = '''
import urllib.request, json, sys

TOKEN = sys.argv[1]

def api(path, method="GET", data=None):
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(f"http://localhost:8123/api/{path}", data=body, headers=headers, method=method)
    try:
        return json.load(urllib.request.urlopen(req, timeout=15))
    except Exception as e:
        return {"error": str(e)}

# Read automations.yaml
with open("/DATA/AppData/homeassistant/config/automations.yaml") as f:
    content = f.read()

# Remove old eco2 automation if exists
lines = content.split("\\n")
new_lines = []
skip = False
for line in lines:
    if "mclh08_eco2_alert" in line or "mclh_08_vysokii_eco2" in line:
        skip = True
    if skip and line.strip().startswith("- id:"):
        skip = False
    if not skip:
        new_lines.append(line)

# Remove trailing empty lines
while new_lines and new_lines[-1].strip() == "":
    new_lines.pop()

# Add new automation with both TTS and mobile notification
new_auto = """
- id: mclh08_eco2_alert
  alias: "MCLH-08: Высокий eCO2 - вентиляция"
  description: "Оповещение при eCO2 > 600 ppm"
  trigger:
    - platform: numeric_state
      entity_id: sensor.datchik_kachestva_vozdukha_eco2
      above: 600
  condition: []
  action:
    - service: notify.mobile_app_mna_lx9
      data:
        title: "MCLH-08: Высокий eCO2"
        message: "Уровень CO2 превышен: >600 ppm. Включите вентиляцию!"
  mode: single
"""

final_content = "\\n".join(new_lines) + new_auto

with open("/DATA/AppData/homeassistant/config/automations.yaml", "w") as f:
    f.write(final_content)

print("Automation updated with TTS + mobile notification")

# Reload automations via API
result = api("services/automation/reload", method="POST", data={})
print(f"Automations reloaded: {result}")

# Verify
states = api("states")
auto = [s for s in states if "mclh08" in s["entity_id"] or "mclh_08" in s["entity_id"]]
for s in auto:
    print(f"  {s['entity_id']} = {s['state']} ({s.get('attributes',{}).get('friendly_name','')})")
'''

with ssh.open_sftp() as sftp:
    with sftp.open('/tmp/ha_update_auto.py', 'w') as f:
        f.write(script)

cmd = f'python3 /tmp/ha_update_auto.py "{TOKEN}"'
stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
exit_code = stdout.channel.recv_exit_status()
out = stdout.read().decode('utf-8', errors='replace').strip()
err = stderr.read().decode('utf-8', errors='replace').strip()
for line in (out + '\n' + err).split('\n'):
    if line.strip():
        print(line.strip())
ssh.close()
