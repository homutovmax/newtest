import paramiko
import json
import time
import urllib.request
import urllib.error
import ssl

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

# Get existing token from auth
stdin, stdout, stderr = ssh.exec_command('docker exec homeassistant cat /config/.storage/auth')
auth = json.loads(stdout.read().decode('utf-8'))
tokens = auth.get("data", {}).get("access_tokens", [])
if not tokens:
    print("No tokens found")
    ssh.close()
    exit()
token = tokens[0].get("token")

ha_url = "http://192.168.1.92:8123"
ctx = ssl._create_unverified_context()

def api_call(method, path, data=None):
    url = f"{ha_url}{path}"
    req = urllib.request.Request(url, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    if data:
        req.data = json.dumps(data).encode('utf-8')
    try:
        r = urllib.request.urlopen(req, timeout=10, context=ctx)
        return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:500]
    except Exception as e:
        return 0, str(e)

# Step 1: Start MQTT config flow
print("Starting MQTT config flow...")
status, result = api_call("POST", "/api/config/config_entries/flow", {"handler": "mqtt"})
print(f"Response: {status}")
print(f"Result: {json.dumps(result, indent=2) if isinstance(result, dict) else result}")

if status != 200 and status != 201:
    print("Failed to start flow")
    ssh.close()
    exit()

flow_id = result.get("flow_id")
step_id = result.get("step_id")
print(f"\nFlow ID: {flow_id}, Step: {step_id}")

# Step 2: Submit broker details
print("\nSubmitting broker config...")
status, result = api_call("POST", f"/api/config/config_entries/flow/{flow_id}", {
    "broker": "127.0.0.1",
    "port": 1883,
    "username": "mqtt",
    "password": "CHANGE_ME",
})
print(f"Response: {status}")
if isinstance(result, dict):
    print(f"Result: {json.dumps(result, indent=2)}")
else:
    print(f"Result: {result}")

if status == 200:
    # Might need to confirm
    if result.get("step_id") == "username" or result.get("step_id") == "broker":
        # Additional step required
        print("\nAdditional step:", result.get("step_id"))
        status, result = api_call("POST", f"/api/config/config_entries/flow/{flow_id}", result.get("data_schema", {}))
        print(f"Response: {status}, Result: {json.dumps(result, indent=2) if isinstance(result, dict) else result}")

ssh.close()
