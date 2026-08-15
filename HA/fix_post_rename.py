import paramiko, json, time

HOST = '192.168.1.92'
USER = 'root'
PASS = 'CHANGE_ME'
TOKEN = 'CHANGE_ME'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username='root', password=PASS, timeout=10)

def mqtt_pub(topic, payload):
    cmd = f'mosquitto_pub -h localhost -p 1883 -u mqtt -P CHANGE_ME -t "{topic}" -m \'{json.dumps(payload)}\''
    ssh.exec_command(cmd, timeout=5)

def mqtt_sub(topic, count=1, timeout=5):
    cmd = f'mosquitto_sub -h localhost -p 1883 -u mqtt -P CHANGE_ME -t "{topic}" -C {count} -W {timeout} -v 2>&1'
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout+5)
    return stdout.read().decode('utf-8', errors='replace').strip()

# 1. Check data from device
print("=== Device data on new topic ===")
result = mqtt_sub("zigbee2mqtt/datchik_kachestva_vozdukha", count=1, timeout=15)
print(result)

# 2. Configure the device (since interview configured_reportings is empty)
print("\n=== Configuring device ===")
mqtt_pub("zigbee2mqtt/bridge/request/device/configure", {
    "ieee_address": "0x00158d0000d9cd2c"
})
time.sleep(3)
result = mqtt_sub("zigbee2mqtt/bridge/response/device/configure", count=1, timeout=10)
print(f"Configure response: {result}")

# 3. Force re-interview
print("\n=== Force re-interview ===")
mqtt_pub("zigbee2mqtt/bridge/request/device/interview", {
    "ieee_address": "0x00158d0000d9cd2c",
    "force": True
})
time.sleep(5)
result = mqtt_sub("zigbee2mqtt/bridge/response/device/interview", count=1, timeout=15)
print(f"Interview response: {result}")

# 4. Try to read battery when device wakes up
print("\n=== Requesting battery read ===")
mqtt_pub("zigbee2mqtt/datchik_kachestva_vozdukha/get", {"battery": ""})
time.sleep(10)
result = mqtt_sub("zigbee2mqtt/datchik_kachestva_vozdukha", count=1, timeout=15)
print(f"Device data after battery request: {result}")

# 5. Check HA states
print("\n=== HA entities ===")
stdin, stdout, stderr = ssh.exec_command(
    'curl -s -H "Authorization: Bearer ' + TOKEN + '" '
    'http://localhost:8123/api/states | python3 -c "import sys,json; d=json.load(sys.stdin); '
    '[print(s[\'entity_id\'], \'=\', s[\'state\']) for s in d if \'datchik\' in s[\'entity_id\'].lower()]\"',
    timeout=15)
print(stdout.read().decode('utf-8', errors='replace').strip())

# 6. Check Z2M recent errors
print("\n=== Recent Z2M errors ===")
stdin2, stdout2, stderr2 = ssh.exec_command(
    'docker logs big-bear-zigbee2mqtt --tail 30 2>&1 | grep -iE "error|fail|warn"',
    timeout=10)
print(stdout2.read().decode('utf-8', errors='replace').strip())

ssh.close()
