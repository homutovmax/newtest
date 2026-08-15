import paramiko, json, time

HOST = '192.168.1.92'
USER = 'root'
PASS = 'CHANGE_ME'
TOKEN = 'CHANGE_ME'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=10)

def api(path, method="GET", data=None):
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(f"http://localhost:8123/api/{path}", data=body, headers=headers, method=method)
    return json.load(urllib.request.urlopen(req, timeout=10))

import urllib.request

# Check config
try:
    config = api("config")
    components = config.get("components", [])
    yash = [c for c in components if "yandex" in c.lower()]
    print(f"Yandex components: {yash}")
    print(f"HA version: {config.get('version')}")
except Exception as e:
    print(f"Error: {e}")

# Try config flow
try:
    result = api("config/config_entries/flow", method="POST", data={
        "handler": "yandex_smart_home",
        "show_advanced_options": True
    })
    print(f"Config flow: {json.dumps(result, ensure_ascii=False)[:500]}")
except urllib.error.HTTPError as e:
    body = e.read().decode()
    print(f"Config flow error: {e.code}: {body[:300]}")
except Exception as e:
    print(f"Config flow error: {e}")

ssh.close()
