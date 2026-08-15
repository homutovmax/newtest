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
    return json.load(urllib.request.urlopen(req, timeout=10))

states = api("states")
for s in states:
    if "media_player" in s["entity_id"]:
        print(f"\\n{s['entity_id']}:")
        print(f"  state: {s['state']}")
        print(f"  attributes: {json.dumps(s.get('attributes',{}), indent=4, ensure_ascii=False)}")

# Also check if HACS has yandex_smart_home
print("\\n=== Checking HACS installed ===")
import urllib.request
req = urllib.request.Request("http://localhost:8123/api/hassio/store/repositories",
    headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"})
try:
    repos = json.load(urllib.request.urlopen(req, timeout=10))
    for r in repos:
        if "yandex" in r.get("name","").lower() or "yandex" in r.get("slug","").lower():
            print(f"  Found: {r.get('name')} ({r.get('slug')})")
except:
    print("  Could not check HACS store")
'''

with ssh.open_sftp() as sftp:
    with sftp.open('/tmp/ha_player_check.py', 'w') as f:
        f.write(script)

stdin, stdout, stderr = ssh.exec_command(f'python3 /tmp/ha_player_check.py "{TOKEN}"', timeout=30)
exit_code = stdout.channel.recv_exit_status()
out = stdout.read().decode('utf-8', errors='replace').strip()
err = stderr.read().decode('utf-8', errors='replace').strip()
for line in (out + '\n' + err).split('\n'):
    if line.strip():
        print(line.strip())
ssh.close()
