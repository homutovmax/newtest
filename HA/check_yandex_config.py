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
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        return {"error": f"{e.code}: {body[:200]}"}

# 1. Check if integration is now available
print("=== Checking integration availability ===")
config = api("config")
components = config.get("components", [])
if "yandex_smart_home" in components:
    print("  yandex_smart_home: AVAILABLE")
else:
    print("  yandex_smart_home: NOT in components list")
    print("  Need to restart HA to load new integration")

# 2. Check config entries
entries = api("config/config_entries/entry")
if isinstance(entries, list):
    yash = [e for e in entries if e.get("domain") == "yandex_smart_home"]
    print(f"\\n=== Config entries ({len(yash)}) ===")
    for e in yash:
        print(f"  Title: {e.get('title')}")
        print(f"  State: {e.get('state')}")
        print(f"  Data: {json.dumps(e.get('data',{}), ensure_ascii=False)[:200]}")
else:
    print(f"  Entries: {entries}")

# 3. Try to start config flow
print("\\n=== Config flow ===")
result = api("config/config_entries/flow", method="POST", data={
    "handler": "yandex_smart_home",
    "show_advanced_options": True
})
print(f"  Flow result: {json.dumps(result, ensure_ascii=False)[:500]}")
'''

with ssh.open_sftp() as sftp:
    with sftp.open('/tmp/ha_yandex_config.py', 'w') as f:
        f.write(script)

cmd = f'python3 /tmp/ha_yandex_config.py "{TOKEN}"'
stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
exit_code = stdout.channel.recv_exit_status()
out = stdout.read().decode('utf-8', errors='replace').strip()
err = stderr.read().decode('utf-8', errors='replace').strip()
for line in (out + '\n' + err).split('\n'):
    if line.strip():
        print(line.strip())
ssh.close()
