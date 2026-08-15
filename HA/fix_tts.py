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
        resp = urllib.request.urlopen(req, timeout=15)
        return json.load(resp)
    except Exception as e:
        return {"error": str(e)}

# 1. Test mobile notification
print("=== Testing mobile notification ===")
result = api("services/notify/mobile_app_mna_lx9", method="POST", data={
    "message": "Внимание! Уровень CO2 превышен: >600 ppm. Включите вентиляцию!",
    "title": "MCLH-08: Высокий eCO2"
})
print(f"  Result: {result}")

# 2. Check configuration.yaml for TTS config
print("\\n=== Checking TTS config ===")
with open("/DATA/AppData/homeassistant/config/configuration.yaml") as f:
    config = f.read()
print(f"  Config: {config[:500]}")

# 3. Check if we can add google translate TTS for Russian
print("\\n=== Adding Google Translate TTS for Russian ===")
# Read config
with open("/DATA/AppData/homeassistant/config/configuration.yaml") as f:
    config_content = f.read()

if "tts:" not in config_content:
    # Add TTS config
    new_config = config_content.rstrip() + "\\n\\ntts:\\n  - platform: google_translate\\n    language: ru\\n"
    with open("/DATA/AppData/homeassistant/config/configuration.yaml", "w") as f:
        f.write(new_config)
    print("  Added google_translate TTS with Russian language")
else:
    print("  TTS config already exists")

# 4. Check HA cloud status
print("\\n=== HA Cloud Status ===")
try:
    result = api("config/cloud")
    print(f"  Cloud: {json.dumps(result, ensure_ascii=False)[:300]}")
except Exception as e:
    print(f"  Error: {e}")

# 5. List all available TTS engines
print("\\n=== TTS Engines ===")
services = api("services")
if isinstance(services, list):
    for s in services:
        if s["domain"] == "tts":
            for k, v in s["services"].items():
                fields = list(v.get("fields", {}).keys())
                print(f"  tts.{k}: {fields}")
'''

with ssh.open_sftp() as sftp:
    with sftp.open('/tmp/ha_fix_tts.py', 'w') as f:
        f.write(script)

cmd = f'python3 /tmp/ha_fix_tts.py "{TOKEN}"'
stdin, stdout, stderr = ssh.exec_command(cmd, timeout=60)
exit_code = stdout.channel.recv_exit_status()
out = stdout.read().decode('utf-8', errors='replace').strip()
err = stderr.read().decode('utf-8', errors='replace').strip()
for line in (out + '\n' + err).split('\n'):
    if line.strip():
        print(line.strip())
ssh.close()
