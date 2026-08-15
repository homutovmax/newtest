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

def api(path):
    req = urllib.request.Request(f"http://localhost:8123/api/{path}",
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"})
    try:
        return json.load(urllib.request.urlopen(req, timeout=10))
    except Exception as e:
        return {"error": str(e)}

# Find all media_player and TTS entities
states = api("states")
if isinstance(states, list):
    # Media players (speakers)
    players = [s for s in states if "media_player" in s["entity_id"]]
    print("=== MEDIA PLAYERS ===")
    for s in players:
        print(f"  {s['entity_id']} = {s['state']} ({s.get('attributes',{}).get('friendly_name','')})")

    # TTS services
    services = api("services")
    if isinstance(services, list):
        tts = [s for s in services if "tts" in s.get("domain","").lower() or "yandex" in s.get("domain","").lower()]
        print("\\n=== TTS/YANDEX SERVICES ===")
        for s in tts:
            print(f"  {s['domain']}.{s['services'].keys() if isinstance(s['services'], dict) else 'N/A'}")

    # Yandex related entities
    yandex = [s for s in states if "yandex" in s["entity_id"].lower()]
    print("\\n=== YANDEX ENTITIES ===")
    for s in yandex:
        print(f"  {s['entity_id']} = {s['state']} ({s.get('attributes',{}).get('friendly_name','')})")

    # All entity IDs containing 'kolonka', 'speaker', 'алес', 'стас', 'колонк'
    print("\\n=== ALL MEDIA/TTS ENTITIES ===")
    for s in states:
        eid = s["entity_id"].lower()
        name = s.get("attributes",{}).get("friendly_name","").lower()
        if any(x in eid or x in name for x in ["speaker", "kolonka", "ттс", "tts", "colonna", "column", "alist", "stas", "alice", "alist", "яндекс", "yandex", "media"]):
            print(f"  {s['entity_id']} = {s['state']} ({s.get('attributes',{}).get('friendly_name','')})")
'''

with ssh.open_sftp() as sftp:
    with sftp.open('/tmp/ha_yandex_check.py', 'w') as f:
        f.write(script)

cmd = f'python3 /tmp/ha_yandex_check.py "{TOKEN}"'
stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
exit_code = stdout.channel.recv_exit_status()
out = stdout.read().decode('utf-8', errors='replace').strip()
err = stderr.read().decode('utf-8', errors='replace').strip()
for line in (out + '\n' + err).split('\n'):
    if line.strip():
        print(line.strip())
ssh.close()
