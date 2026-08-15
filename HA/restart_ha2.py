import paramiko, json, time

HOST = '192.168.1.92'
USER = 'root'
PASS = 'CHANGE_ME'
TOKEN = 'CHANGE_ME'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=10)

# Restart HA via docker
print("Restarting HA container...")
stdin, stdout, stderr = ssh.exec_command('docker restart homeassistant 2>&1', timeout=30)
out = stdout.read().decode('utf-8', errors='replace').strip()
print(f"  {out}")

print("Waiting 30s for startup...")
time.sleep(30)

# Check if HA is up
import urllib.request
for i in range(6):
    try:
        req = urllib.request.Request("http://localhost:8123/api/",
            headers={"Authorization": f"Bearer {TOKEN}"})
        resp = urllib.request.urlopen(req, timeout=5)
        data = json.load(resp)
        print(f"  HA is up: {data}")
        break
    except Exception as e:
        print(f"  Attempt {i+1}: {e}")
        time.sleep(15)

# Wait more and check components
time.sleep(20)
try:
    req = urllib.request.Request("http://localhost:8123/api/config",
        headers={"Authorization": f"Bearer {TOKEN}"})
    config = json.load(urllib.request.urlopen(req, timeout=10))
    components = config.get("components", [])
    yash = [c for c in components if "yandex" in c.lower()]
    print(f"\n  Yandex components: {yash}")
    print(f"  HA version: {config.get('version')}")
except Exception as e:
    print(f"  Config check error: {e}")

ssh.close()
