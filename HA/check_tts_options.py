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
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        return {"error": f"{e.code}: {body}"}

# 1. List all TTS entities and their supported languages
states = api("states")
print("=== ALL TTS ENTITIES ===")
tts_entities = [s for s in states if s["entity_id"].startswith("tts.")]
for s in tts_entities:
    print(f"  {s['entity_id']}:")
    print(f"    state: {s['state']}")
    print(f"    attrs: {json.dumps(s.get('attributes',{}), ensure_ascii=False)}")

# 2. List all media_player entities with full attributes
print("\\n=== MEDIA PLAYERS ===")
mp_entities = [s for s in states if s["entity_id"].startswith("media_player.")]
for s in mp_entities:
    print(f"  {s['entity_id']}:")
    print(f"    state: {s['state']}")
    print(f"    attrs: {json.dumps(s.get('attributes',{}), ensure_ascii=False)[:200]}")

# 3. Try tts.speak with google translate (English)
print("\\n=== Testing tts.speak with Google TTS ===")
try:
    result = api("services/tts/speak", method="POST", data={
        "media_player_entity_id": "media_player.h96_94_2",
        "entity_id": "tts.google_translate_en_com",
        "message": "Warning! CO2 level is high. Ventilation needed."
    })
    print(f"  Result: {result}")
except Exception as e:
    print(f"  Error: {e}")

# 4. Try notify services
print("\\n=== NOTIFY SERVICES ===")
services = api("services")
if isinstance(services, list):
    for s in services:
        if s["domain"] == "notify":
            for k, v in s["services"].items():
                fields = list(v.get("fields", {}).keys())
                print(f"  notify.{k}: {fields}")

# 5. Try mobile notification
print("\\n=== Testing mobile notification ===")
try:
    result = api("services/notify/send_message", method="POST", data={
        "message": "Внимание! CO2 > 600 ppm. Нужно включить вентиляцию!",
        "title": "MCLH-08: Высокий eCO2",
        "target": ["notify.mobile_app_mna_lx9"]
    })
    print(f"  Result: {result}")
except Exception as e:
    print(f"  Error: {e}")
'''

with ssh.open_sftp() as sftp:
    with sftp.open('/tmp/ha_tts_check.py', 'w') as f:
        f.write(script)

cmd = f'python3 /tmp/ha_tts_check.py "{TOKEN}"'
stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
exit_code = stdout.channel.recv_exit_status()
out = stdout.read().decode('utf-8', errors='replace').strip()
err = stderr.read().decode('utf-8', errors='replace').strip()
for line in (out + '\n' + err).split('\n'):
    if line.strip():
        print(line.strip())
ssh.close()
