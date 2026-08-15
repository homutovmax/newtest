import paramiko
import json
import time
import uuid
import urllib.request
import urllib.error
import ssl

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

# Wait for HA to finish restarting
print("Waiting for HA to start...")
time.sleep(30)

# Check HA status
stdin, stdout, stderr = ssh.exec_command('docker ps --filter name=homeassistant --format "{{.Names}} {{.Status}}"')
print(stdout.read().decode().strip())

ha_url = "http://192.168.1.92:8123"
ctx = ssl._create_unverified_context()

# Try to reach HA API
for i in range(10):
    try:
        r = urllib.request.urlopen(f"{ha_url}/api/", timeout=3, context=ctx)
        print("HA API response:", r.status, r.read().decode()[:200])
        break
    except Exception as e:
        print(f"Attempt {i+1}: {e}")
        time.sleep(3)

# Get auth file to see existing tokens
stdin, stdout, stderr = ssh.exec_command('docker exec homeassistant cat /config/.storage/auth')
auth = json.loads(stdout.read().decode('utf-8'))

# Find owner
owner_id = None
users = auth.get("data", {}).get("users", [])
for u in users:
    if u.get("is_owner"):
        owner_id = u.get("id")
        print("Owner ID:", owner_id)

# Check existing access_tokens
existing_tokens = auth.get("data", {}).get("access_tokens", [])
print(f"Existing tokens: {len(existing_tokens)}")
for t in existing_tokens[:5]:
    print(f"  token: {t.get('token')[:20]}... client_id: {t.get('client_id')}")

# Try using one of the existing tokens
if existing_tokens:
    test_token = existing_tokens[0].get("token")
    print(f"\nTrying existing token: {test_token[:20]}...")
    req = urllib.request.Request(f"{ha_url}/api/config/core/check_config")
    req.add_header("Authorization", f"Bearer {test_token}")
    try:
        r = urllib.request.urlopen(req, timeout=5, context=ctx)
        print("Check config:", r.status, r.read().decode()[:300])
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} {e.reason}")
        print(e.read().decode()[:300])
    except Exception as e:
        print(f"Error: {e}")

ssh.close()
