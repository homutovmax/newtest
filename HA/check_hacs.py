import paramiko, json

HOST = '192.168.1.92'
USER = 'root'
PASS = 'CHANGE_ME'
TOKEN = 'CHANGE_ME'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=10)

script = '''
import urllib.request, json, sys, os, subprocess

TOKEN = sys.argv[1]

def api(path, method="GET", data=None):
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(f"http://localhost:8123/api/{path}", data=body, headers=headers, method=method)
    try:
        return json.load(urllib.request.urlopen(req, timeout=15))
    except Exception as e:
        return {"error": str(e)}

# 1. Check HACS
print("=== HACS Status ===")
hacs_dir = "/DATA/AppData/homeassistant/config/custom_components/hacs"
if os.path.exists(hacs_dir):
    print("  HACS installed")
    # Check HACS version
    try:
        with open(f"{hacs_dir}/manifest.json") as f:
            manifest = json.load(f)
            print(f"  Version: {manifest.get('version', '?')}")
    except:
        print("  Could not read manifest")
else:
    print("  HACS NOT installed")

# 2. Check if yandex_smart_home already exists
yash_dir = "/DATA/AppData/homeassistant/config/custom_components/yandex_smart_home"
if os.path.exists(yash_dir):
    print("\\n=== yandex_smart_home already installed ===")
    try:
        with open(f"{yash_dir}/manifest.json") as f:
            manifest = json.load(f)
            print(f"  Version: {manifest.get('version', '?')}")
    except:
        print("  Could not read manifest")
else:
    print("\\n=== yandex_smart_home NOT installed ===")
    print("  Will install via git...")

# 3. Check HA config for issues
print("\\n=== HA Config Check ===")
result = api("config/core/check_config", method="POST")
print(f"  Config valid: {result}")

# 4. Check current automations
states = api("states")
auto_states = [s for s in states if s["entity_id"].startswith("automation.")]
print(f"\\n=== Automations ({len(auto_states)}) ===")
for s in auto_states:
    print(f"  {s['entity_id']}: {s['state']} ({s.get('attributes',{}).get('friendly_name','')})")
'''

with ssh.open_sftp() as sftp:
    with sftp.open('/tmp/ha_hacs_check.py', 'w') as f:
        f.write(script)

cmd = f'python3 /tmp/ha_hacs_check.py "{TOKEN}"'
stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
exit_code = stdout.channel.recv_exit_status()
out = stdout.read().decode('utf-8', errors='replace').strip()
err = stderr.read().decode('utf-8', errors='replace').strip()
for line in (out + '\n' + err).split('\n'):
    if line.strip():
        print(line.strip())
ssh.close()
