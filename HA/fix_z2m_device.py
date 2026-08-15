import paramiko, json, time, re

HOST = '192.168.1.92'
USER = 'root'
PASS = 'CHANGE_ME'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=10)

# Check Z2M configuration
print("=== Z2M configuration.yaml ===")
stdin, stdout, stderr = ssh.exec_command('docker exec big-bear-zigbee2mqtt cat /app/configuration.yaml 2>/dev/null || cat /DATA/AppData/big-bear-zigbee2mqtt/configuration.yaml 2>/dev/null', timeout=10)
print(stdout.read().decode('utf-8', errors='replace').strip()[:3000])

# Check for Z2M data directory structure
print("\n=== Z2M data files ===")
stdin, stdout, stderr = ssh.exec_command('find /DATA/AppData/big-bear-zigbee2mqtt -type f -name "*.yaml" -o -name "*.json" -o -name "*.db" 2>/dev/null | head -20', timeout=10)
print(stdout.read().decode('utf-8', errors='replace').strip())

# Check coordinator state
print("\n=== Z2M devices file ===")
stdin, stdout, stderr = ssh.exec_command('find /DATA/AppData/big-bear-zigbee2mqtt -name "devices.yaml" -o -name "device.yaml" 2>/dev/null', timeout=10)
devices_paths = stdout.read().decode('utf-8', errors='replace').strip()
print(f"Devices files: {devices_paths}")

# Try to find Z2M database or state
stdin, stdout, stderr = ssh.exec_command('ls -la /DATA/AppData/big-bear-zigbee2mqtt/ 2>/dev/null', timeout=10)
print(f"\n=== Z2M data directory ===")
print(stdout.read().decode('utf-8', errors='replace').strip())

# Try using mosquitto_pub for rename more carefully
print("\n=== Attempting rename via MQTT ===")
# First check if device responds to any command
cmd = 'mosquitto_pub -h localhost -p 1883 -u mqtt -P CHANGE_ME -t "zigbee2mqtt/bridge/request/device/rename" -m \'{"from":"","to":"datchik_kachestva_vozdukha","ieee_address":"0x00158d0000d9cd2c"}\''
stdin, stdout, stderr = ssh.exec_command(cmd, timeout=5)
print(f"Publish exit code: {stdout.channel.recv_exit_status() if hasattr(stdout, 'channel') else 'N/A'}")

# Wait and check response
time.sleep(3)
stdin2, stdout2, stderr2 = ssh.exec_command(
    'mosquitto_sub -h localhost -p 1883 -u mqtt -P CHANGE_ME '
    '-t zigbee2mqtt/bridge/response/device/rename -C 1 -W 5 -v 2>&1',
    timeout=10)
response = stdout2.read().decode('utf-8', errors='replace').strip()
print(f"Rename response: {response}")

# Check device info after rename
stdin3, stdout3, stderr3 = ssh.exec_command(
    'mosquitto_sub -h localhost -p 1883 -u mqtt -P CHANGE_ME '
    '-t zigbee2mqtt/bridge/devices -C 1 -W 5 -v 2>&1',
    timeout=10)
devices = stdout3.read().decode('utf-8', errors='replace').strip()
mclh_idx = devices.find("0x00158d0000d9cd2c")
if mclh_idx >= 0:
    start = devices.rfind("{", 0, mclh_idx)
    end = devices.find("}", mclh_idx)
    print(f"Device info: {devices[start:end+1]}")

# Check Z2M logs for rename
stdin4, stdout4, stderr4 = ssh.exec_command(
    'docker logs big-bear-zigbee2mqtt --tail 20 2>&1 | grep -i "rename\|mclh\|datchik\|00158d"',
    timeout=10)
print(f"\n=== Z2M recent logs ===")
print(stdout4.read().decode('utf-8', errors='replace').strip())

ssh.close()
