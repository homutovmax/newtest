import paramiko, json

HOST = '192.168.1.92'
USER = 'root'
PASS = 'CHANGE_ME'
TOKEN = 'CHANGE_ME'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=10)

script = '''
import json, sys

with open("/DATA/AppData/homeassistant/config/.storage/core.config_entries") as f:
    data = json.load(f)

entries = data.get("data", data).get("entries", [])
for e in entries:
    domain = e.get("domain", "")
    title = e.get("title", "")
    state = e.get("state", "")
    print(f"{domain}: {title} [{state}]")

print("\\n=== ALL ENTITIES (searching for speakers) ===")
import urllib.request
req = urllib.request.Request("http://localhost:8123/api/states",
    headers={"Authorization": "Bearer ''' + TOKEN + '''", "Content-Type": "application/json"})
states = json.load(urllib.request.urlopen(req, timeout=10))
for s in states:
    eid = s["entity_id"]
    name = s.get("attributes", {}).get("friendly_name", "")
    if any(x in eid.lower() + name.lower() for x in ["media", "tts", "sound", "speaker", "station", "yandex", "alice", "alist"]):
        print(f"  {eid} = {s['state']} ({name})")

print("\\n=== TTS cloud_say service details ===")
req2 = urllib.request.Request("http://localhost:8123/api/services",
    headers={"Authorization": "Bearer ''' + TOKEN + '''", "Content-Type": "application/json"})
services = json.load(urllib.request.urlopen(req2, timeout=10))
for s in services:
    if s["domain"] == "tts":
        svc = s["services"]
        for k, v in svc.items():
            print(f"  tts.{k}: {v.get('name','')}")
            fields = v.get("fields", {})
            for fk, fv in fields.items():
                print(f"    {fk}: {fv.get('description','')} (required={fv.get('required', False)})")
'''

with ssh.open_sftp() as sftp:
    with sftp.open('/tmp/ha_check2.py', 'w') as f:
        f.write(script)

stdin, stdout, stderr = ssh.exec_command(f'python3 /tmp/ha_check2.py', timeout=30)
exit_code = stdout.channel.recv_exit_status()
out = stdout.read().decode('utf-8', errors='replace').strip()
err = stderr.read().decode('utf-8', errors='replace').strip()
for line in (out + '\n' + err).split('\n'):
    if line.strip():
        print(line.strip())
ssh.close()
