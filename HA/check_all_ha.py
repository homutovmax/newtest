import paramiko, json

HOST = '192.168.1.92'
USER = 'root'
PASS = 'CHANGE_ME'
TOKEN = 'CHANGE_ME'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=10)

# Upload comprehensive check script
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

# 1. HA config
config = api("config")
print("=== HA CONFIG ===")
print(f"Version: {config.get('version','?')}")
print(f"Components: {[c for c in config.get('components',[]) if 'mqtt' in c.lower() or 'zigbee' in c.lower()]}")

# 2. All states - find MCLH-08 entities
states = api("states")
if isinstance(states, list):
    mclh = [s for s in states if "00158d0000d9cd2c" in s["entity_id"]]
    print(f"\\n=== MCLH-08 ENTITIES ({len(mclh)}) ===")
    for s in mclh:
        print(f"  {s['entity_id']} = {s['state']}")
    
    datchik = [s for s in states if "datchik_kachestva" in s["entity_id"]]
    print(f"\\n=== DATCHIK ENTITIES ({len(datchik)}) ===")
    for s in datchik:
        print(f"  {s['entity_id']} = {s['state']}")

# 3. Check MQTT config entries
entries = api("config/config_entries/entry")
if isinstance(entries, list):
    mqtt_entries = [e for e in entries if e.get("domain") == "mqtt"]
    print(f"\\n=== MQTT INTEGRATION ({len(mqtt_entries)}) ===")
    for e in mqtt_entries:
        print(f"  Title: {e.get('title','?')}")
        print(f"  Source: {e.get('source','?')}")
        print(f"  State: {e.get('state','?')}")
        print(f"  Data: {json.dumps(e.get('data',{}), indent=4)}")
else:
    print(f"\\n=== CONFIG ENTRIES ===")
    print(entries)

# 4. Check for errors
print(f"\\n=== LOGS (ERRORS) ===")
log = api("error_log")
if log:
    lines = log.split("\\n") if isinstance(log, str) else [str(log)]
    errors = [l for l in lines if "ERROR" in l.upper() or "WARNING" in l.upper()]
    for e in errors[-20:]:
        print(f"  {e}")
'''

with ssh.open_sftp() as sftp:
    with sftp.open('/tmp/ha_check.py', 'w') as f:
        f.write(script)

stdin, stdout, stderr = ssh.exec_command(f'python3 /tmp/ha_check.py "{TOKEN}"', timeout=30)
exit_code = stdout.channel.recv_exit_status()
out = stdout.read().decode('utf-8', errors='replace').strip()
err = stderr.read().decode('utf-8', errors='replace').strip()
# Filter out garbage /tmp from debug
lines = (out + '\n' + err).split('\n')
for line in lines:
    stripped = line.strip()
    if stripped and '/tmp/python' not in stripped:
        print(stripped)
ssh.close()
