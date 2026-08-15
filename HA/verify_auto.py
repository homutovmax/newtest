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
    return json.load(urllib.request.urlopen(req, timeout=15))

# 1. Check automations
states = api("states")
auto_states = [s for s in states if s["entity_id"].startswith("automation.")]
print("=== AUTOMATIONS ===")
for s in auto_states:
    print(f"  {s['entity_id']} = {s['state']} ({s.get('attributes',{}).get('friendly_name','')})")

# 2. Check if tts.cloud_say service works
print("\\n=== Testing TTS ===")
try:
    result = api("services/tts/cloud_say", method="POST", data={
        "entity_id": "media_player.h96_94_2",
        "message": "Тест TTS. Проверка работоспособности."
    })
    print("  TTS call: OK")
except Exception as e:
    print(f"  TTS call failed: {e}")

# 3. Check HA cloud status (for TTS)
print("\\n=== HA Cloud ===")
try:
    cloud = api("config/cloud")
    print(f"  Cloud: {cloud}")
except:
    print("  Cloud status unavailable")

# 4. Check automations.yaml content
with open("/DATA/AppData/homeassistant/config/automations.yaml") as f:
    content = f.read()
print(f"\\n=== automations.yaml ({len(content)} chars) ===")
if "eco2" in content.lower() or "mclh08" in content.lower():
    print("  eco2 automation found")
else:
    print("  WARNING: eco2 automation NOT found")
'''

with ssh.open_sftp() as sftp:
    with sftp.open('/tmp/ha_verify_auto.py', 'w') as f:
        f.write(script)

cmd = f'python3 /tmp/ha_verify_auto.py "{TOKEN}"'
stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
exit_code = stdout.channel.recv_exit_status()
out = stdout.read().decode('utf-8', errors='replace').strip()
err = stderr.read().decode('utf-8', errors='replace').strip()
for line in (out + '\n' + err).split('\n'):
    if line.strip():
        print(line.strip())
ssh.close()
