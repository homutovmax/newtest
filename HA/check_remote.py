import paramiko, json, sys

TOKEN = 'CHANGE_ME'
HOST = '192.168.1.92'
USER = 'root'
PASS = 'CHANGE_ME'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=10)

# 1. Check Docker containers
print("=== DOCKER CONTAINERS ===")
stdin, stdout, stderr = ssh.exec_command('docker ps --format "{{.Names}} {{.Status}}"', timeout=10)
print(stdout.read().decode().strip())

# 2. Check HA states
print("\n=== HA STATES ===")
stdin, stdout, stderr = ssh.exec_command(
    'curl -s -H "Authorization: Bearer ' + TOKEN + '" '
    '-H "Content-Type: application/json" http://localhost:8123/api/states',
    timeout=15)
data = json.loads(stdout.read().decode())
print(f"Total entities: {len(data)}")

mclh = [s for s in data if "mclh" in s["entity_id"].lower() or "00158d" in s["entity_id"]]
print(f"MCLH-08 entities: {len(mclh)}")
for s in mclh:
    print(f"  {s['entity_id']} = {s['state']}")

# Print all sensors
sensors = [s for s in data if s["entity_id"].startswith("sensor.")]
print(f"\nAll sensors ({len(sensors)}):")
for s in sensors:
    print(f"  {s['entity_id']} = {s['state']}")

# 3. Check Z2M devices
print("\n=== Z2M DEVICES ===")
stdin, stdout, stderr = ssh.exec_command(
    'mosquitto_sub -h localhost -p 1883 -u mqtt -P CHANGE_ME '
    '-t zigbee2mqtt/bridge/devices -C 1 -W 5 -v 2>&1', timeout=15)
z2m_raw = stdout.read().decode('utf-8', errors='replace').strip()

# Parse to find MCLH-08
if "00158d0000d9cd2c" in z2m_raw:
    print("MCLH-08 (0x00158d0000d9cd2c) FOUND in Z2M!")
    import re
    # Extract the device info
    start = z2m_raw.find("0x00158d0000d9cd2c")
    # Find surrounding JSON
    bracket_start = z2m_raw.rfind("{", 0, start)
    bracket_end = z2m_raw.find("}", start)
    if bracket_start >= 0 and bracket_end > bracket_start:
        dev_info = z2m_raw[bracket_start:bracket_end+1]
        print(f"  Device info: {dev_info}")
else:
    print("MCLH-08 NOT found in Z2M bridge devices!")
    print(f"Raw Z2M output (first 2000 chars): {z2m_raw[:2000]}")

# 4. Check configuration.yaml
print("\n=== HA CONFIGURATION.YAML ===")
stdin, stdout, stderr = ssh.exec_command(
    'cat /DATA/AppData/homeassistant/config/configuration.yaml 2>&1', timeout=10)
print(stdout.read().decode().strip())

# 5. Check HA core config for MQTT
print("\n=== HA CORE CONFIG ===")
stdin, stdout, stderr = ssh.exec_command(
    'curl -s -H "Authorization: Bearer ' + TOKEN + '" '
    'http://localhost:8123/api/config', timeout=10)
config = json.loads(stdout.read().decode())
print(f"Version: {config.get('version')}")
mqtt_components = [c for c in config.get('components', []) if 'mqtt' in c.lower()]
print(f"MQTT components: {mqtt_components}")

# 6. Check HA services
print("\n=== HA SERVICES ===")
stdin, stdout, stderr = ssh.exec_command(
    'curl -s -H "Authorization: Bearer ' + TOKEN + '" '
    'http://localhost:8123/api/services', timeout=10)
services = json.loads(stdout.read().decode())
mqtt_services = [s for s in services if 'mqtt' in s.get('domain', '').lower()]
print(f"MQTT services: {len(mqtt_services)}")
for s in mqtt_services[:5]:
    print(f"  {s.get('domain')}: {[x.get('service') for x in s.get('services', {}).values()][:5]}")

ssh.close()
print("\n=== CHECK COMPLETE ===")
