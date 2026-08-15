import paramiko, json, time

HOST = '192.168.1.92'
USER = 'root'
PASS = 'CHANGE_ME'
TOKEN = 'CHANGE_ME'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=10)

def run(cmd, timeout=15):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    return out, err

# Step 1: Restart HA via API
print("=== Restarting Home Assistant ===")
import urllib.request
headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
req = urllib.request.Request("http://localhost:8123/api/services/homeassistant/restart",
    data=json.dumps({}).encode(), headers=headers, method="POST")
try:
    urllib.request.urlopen(req, timeout=15)
    print("  Restart signal sent")
except Exception as e:
    print(f"  Error: {e}")

# Step 2: Wait for HA to come back
print("\n=== Waiting for HA to restart ===")
time.sleep(20)

for attempt in range(12):
    try:
        req = urllib.request.Request("http://localhost:8123/api/",
            headers={"Authorization": f"Bearer {TOKEN}"})
        resp = urllib.request.urlopen(req, timeout=5)
        data = json.load(resp)
        if data.get("message") == "API running.":
            print(f"  HA is back (attempt {attempt+1})")
            break
    except:
        print(f"  Waiting... (attempt {attempt+1})")
        time.sleep(10)
else:
    print("  HA did not restart in time")

# Step 3: Check if yandex_smart_home loaded
time.sleep(10)
req = urllib.request.Request("http://localhost:8123/api/config",
    headers={"Authorization": f"Bearer {TOKEN}"})
config = json.load(urllib.request.urlopen(req, timeout=10))
components = config.get("components", [])
if "yandex_smart_home" in components:
    print("\n  yandex_smart_home: LOADED!")
else:
    print(f"\n  yandex_smart_home: NOT loaded")
    print(f"  Components: {[c for c in components if 'yandex' in c.lower()]}")

# Step 4: Try config flow
print("\n=== Starting config flow ===")
req = urllib.request.Request("http://localhost:8123/api/config/config_entries/flow",
    data=json.dumps({"handler": "yandex_smart_home", "show_advanced_options": True}).encode(),
    headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
    method="POST")
try:
    result = json.load(urllib.request.urlopen(req, timeout=15))
    print(f"  Flow: {json.dumps(result, ensure_ascii=False)[:500]}")
except urllib.error.HTTPError as e:
    body = e.read().decode()
    print(f"  Error: {e.code}: {body[:300]}")
except Exception as e:
    print(f"  Error: {e}")

ssh.close()
