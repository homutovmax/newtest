import paramiko, json, time, re

HOST = '192.168.1.92'
USER = 'root'
PASS = 'CHANGE_ME'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=10)

def mqtt_pub(topic, payload):
    cmd = f'mosquitto_pub -h localhost -p 1883 -u mqtt -P CHANGE_ME -t "{topic}" -m \'{json.dumps(payload)}\''
    ssh.exec_command(cmd, timeout=5)

def mqtt_sub(topic, count=1, timeout=5):
    cmd = f'mosquitto_sub -h localhost -p 1883 -u mqtt -P CHANGE_ME -t "{topic}" -C {count} -W {timeout} -v 2>&1'
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout+5)
    return stdout.read().decode('utf-8', errors='replace').strip()

def api_get(path):
    cmd = f'curl -s -H "Authorization: Bearer CHANGE_ME" "http://localhost:8123{path}"'
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=10)
    try:
        return json.loads(stdout.read().decode())
    except:
        return stdout.read().decode()

print("=== Current MCLH-08 state ===")
# Get current device info
devices_raw = mqtt_sub("zigbee2mqtt/bridge/devices", count=1, timeout=5)
mclh_start = devices_raw.find("0x00158d0000d9cd2c")
if mclh_start >= 0:
    bracket_start = devices_raw.rfind("{", 0, mclh_start)
    bracket_end = devices_raw.find("}", mclh_start)
    if bracket_start >= 0 and bracket_end > bracket_start:
        print(f"MCLH-08 device info: {devices_raw[bracket_start:bracket_end+1]}")

# Step 1: Rename the device
print("\n=== Step 1: Rename MCLH-08 ===")
topic = "zigbee2mqtt/bridge/request/device/rename"
payload = {
    "from": "",
    "to": "datchik_kachestva_vozdukha",
    "ieee_address": "0x00158d0000d9cd2c",
    "homeassistant_rename": True
}
mqtt_pub(topic, payload)
time.sleep(2)

# Check result
result = mqtt_sub("zigbee2mqtt/bridge/response/device/rename", count=1, timeout=3)
print(f"Rename result: {result}")

# Step 2: Check if device MQTT data is flowing
print("\n=== Step 2: Check device data ===")
result = mqtt_sub("zigbee2mqtt/datchik_kachestva_vozdukha", count=1, timeout=10)
print(f"Device data: {result}")

# Step 3: Re-interview if needed
print("\n=== Step 3: Force re-interview ===")
topic = "zigbee2mqtt/bridge/request/device/interview"
payload = {
    "ieee_address": "0x00158d0000d9cd2c",
    "force": True
}
mqtt_pub(topic, payload)
time.sleep(3)
result = mqtt_sub("zigbee2mqtt/bridge/response/device/interview", count=1, timeout=5)
print(f"Interview response: {result}")

# Step 4: Try to configure reporting  
print("\n=== Step 4: Configure reporting ===")
topic = "zigbee2mqtt/bridge/request/device/reporting/configure"
payload = {
    "ieee_address": "0x00158d0000d9cd2c",
}
mqtt_pub(topic, payload)
time.sleep(3)
result = mqtt_sub("zigbee2mqtt/bridge/response/device/reporting/configure", count=1, timeout=10)
print(f"Configure reporting response: {result}")

# Step 5: Re-check HA states
print("\n=== Step 5: HA states after fix ===")
states = api_get("/api/states")
if isinstance(states, list):
    mclh = [s for s in states if "datchik" in s["entity_id"].lower() or "00158d" in s["entity_id"]]
    print(f"Matching entities: {len(mclh)}")
    for s in mclh:
        print(f"  {s['entity_id']} = {s['state']}")

ssh.close()
print("\n=== Fix complete ===")
