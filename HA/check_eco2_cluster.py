import paramiko, json

HOST = '192.168.1.92'
USER = 'root'
PASS = 'CHANGE_ME'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=10)

def exec(cmd, timeout=10):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    return stdout.read().decode('utf-8', errors='replace').strip()

# 1. Get device definition from Z2M
print("=== Device info from bridge ===")
devices = exec(
    'mosquitto_sub -h localhost -p 1883 -u mqtt -P CHANGE_ME '
    '-t zigbee2mqtt/bridge/devices -C 1 -W 5 -v 2>&1', timeout=10)
mclh_idx = devices.find("0x00158d0000d9cd2c")
if mclh_idx >= 0:
    start = devices.rfind("{", 0, mclh_idx)
    end = devices.find("}", mclh_idx)
    print(devices[start:end+1])

# 2. Get full device definition from Z2M's internal definitions
print("\n=== Z2M device definition for MCLH-08 ===")
stdin, stdout, stderr = ssh.exec_command(
    'docker exec big-bear-zigbee2mqtt find /app -name "*.js" -path "*/devices/*" 2>/dev/null | head -20',
    timeout=10)
print(stdout.read().decode('utf-8', errors='replace').strip())

# 3. Look for MCLH-08 definition in Z2M
stdin2, stdout2, stderr2 = ssh.exec_command(
    'docker exec big-bear-zigbee2mqtt grep -r -l "MCLH-08\|Nexturn\|VOC_Sensor" /app/devices/ 2>/dev/null || '
    'docker exec big-bear-zigbee2mqtt find /app -name "*.js" -exec grep -l "MCLH-08\|VOC_Sensor" {} \\; 2>/dev/null | head -5',
    timeout=15)
print(f"\nDefinition files: {stdout2.read().decode('utf-8', errors='replace').strip()}")

# 4. Try to read the zigbee-herdsman-converters device definition
stdin3, stdout3, stderr3 = ssh.exec_command(
    'docker exec big-bear-zigbee2mqtt find /app/node_modules -path "*/zigbee-herdsman-converters/devices" -type d 2>/dev/null | head -5',
    timeout=10)
zdir = stdout3.read().decode('utf-8', errors='replace').strip()
if zdir:
    print(f"\nHerdsman devices dir: {zdir}")
    stdin4, stdout4, stderr4 = ssh.exec_command(
        f'docker exec big-bear-zigbee2mqtt grep -l "MCLH-08\|VOC_Sensor" {zdir}/*.js 2>/dev/null | head -5',
        timeout=10)
    print(f"MCLH files: {stdout4.read().decode('utf-8', errors='replace').strip()}")

# 5. Check device current state and data
print("\n=== Current device data (latest report) ===")
data = exec(
    'mosquitto_sub -h localhost -p 1883 -u mqtt -P CHANGE_ME '
    '-t zigbee2mqtt/datchik_kachestva_vozdukha -C 1 -W 15 -v 2>&1', timeout=20)
print(data)

# 6. Try to read specific attributes via ZCL
print("\n=== Try to read eCO2 cluster info ===")
# The eCO2 might be on cluster 0xFC11 (custom) or similar
# First check what attributes are available
exec('mosquitto_pub -h localhost -p 1883 -u mqtt -P CHANGE_ME -t "zigbee2mqtt/datchik_kachestva_vozdukha/get" -m \'{"eco2":""}\'', timeout=5)

import time
time.sleep(8)
data2 = exec(
    'mosquitto_sub -h localhost -p 1883 -u mqtt -P CHANGE_ME '
    '-t zigbee2mqtt/datchik_kachestva_vozdukha -C 1 -W 10 -v 2>&1', timeout=15)
print(f"After get: {data2}")

ssh.close()
