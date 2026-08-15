import paramiko, json

HOST = '192.168.1.92'
USER = 'root'
PASS = 'CHANGE_ME'
TOKEN = 'CHANGE_ME'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username='root', password=PASS, timeout=10)

# 1. Docker containers
print("=== DOCKER CONTAINERS ===")
stdin, stdout, stderr = ssh.exec_command('docker ps --format "{{.Names}} {{.Status}}"', timeout=10)
print(stdout.read().decode().strip())

# 2. HA version and config
print("\n=== HA CONFIG ===")
stdin, stdout, stderr = ssh.exec_command(
    'curl -s -H "Authorization: Bearer ' + TOKEN + '" http://localhost:8123/api/config 2>&1',
    timeout=10)
raw = stdout.read().decode('utf-8', errors='replace').strip()
print(f"Raw config: {raw[:500]}")

# 3. Z2M device info
print("\n=== Z2M MCLH-08 DEVICE ===")
stdin, stdout, stderr = ssh.exec_command(
    'mosquitto_sub -h localhost -p 1883 -u mqtt -P CHANGE_ME '
    '-t zigbee2mqtt/bridge/devices -C 1 -W 5 -v 2>&1',
    timeout=10)
devices = stdout.read().decode('utf-8', errors='replace').strip()
mclh_idx = devices.find("0x00158d0000d9cd2c")
if mclh_idx >= 0:
    start = devices.rfind("{", 0, mclh_idx)
    end = devices.find("}", mclh_idx)
    import re
    info = devices[start:end+1]
    fn = re.search(r'"friendly_name":"([^"]+)"', info)
    iv = re.search(r'"interview_completed":(true|false)', info)
    ist = re.search(r'"interview_state":"([^"]+)"', info)
    print(f"Friendly name: {fn.group(1) if fn else '?'}")
    print(f"Interview completed: {iv.group(1) if iv else '?'}")
    print(f"Interview state: {ist.group(1) if ist else '?'}")

# 4. HA MCLH/datchik entities
print("\n=== DATCHIK ENTITIES ===")
stdin, stdout, stderr = ssh.exec_command(
    'curl -s -H "Authorization: Bearer ' + TOKEN + '" '
    'http://localhost:8123/api/states | python3 -c "import sys,json; d=json.load(sys.stdin); '
    '[print(s[\'entity_id\'], \'=\', s[\'state\']) for s in d if \'datchik\' in s[\'entity_id\'].lower()]"',
    timeout=15)
print(stdout.read().decode('utf-8', errors='replace').strip())

# 5. Unavailable entities
print("\n=== UNAVAILABLE ENTITIES ===")
stdin, stdout, stderr = ssh.exec_command(
    'curl -s -H "Authorization: Bearer ' + TOKEN + '" '
    'http://localhost:8123/api/states | python3 -c "import sys,json; d=json.load(sys.stdin); '
    'unavail = [s for s in d if s[\'state\'] == \'unavailable\']; '
    'print(f\'Total unavailable: {len(unavail)}\'); '
    '[print(s[\'entity_id\']) for s in unavail]"',
    timeout=15)
print(stdout.read().decode('utf-8', errors='replace').strip())

# 6. Z2M health check
print("\n=== Z2M HEALTH ===")
stdin, stdout, stderr = ssh.exec_command(
    'mosquitto_sub -h localhost -p 1883 -u mqtt -P CHANGE_ME '
    '-t zigbee2mqtt/bridge/health -C 1 -W 5 -v 2>&1',
    timeout=10)
print(stdout.read().decode('utf-8', errors='replace').strip())

# 7. Check core MQTT config  
print("\n=== MQTT CONFIG CHECK ===")
stdin, stdout, stderr = ssh.exec_command(
    'docker exec homeassistant cat /config/configuration.yaml 2>&1',
    timeout=10)
print(stdout.read().decode('utf-8', errors='replace').strip())

ssh.close()
