import paramiko, re

HOST = '192.168.1.92'
USER = 'root'
PASS = 'CHANGE_ME'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=10)
sftp = ssh.open_sftp()

print("=== Reading Z2M configuration.yaml ===")
remote_path = '/DATA/AppData/big-bear-zigbee2mqtt/data/configuration.yaml'
with sftp.open(remote_path, 'r') as f:
    content = f.read().decode('utf-8')

print("Current devices section:")
# Find and print devices section
devices_start = content.find('devices:')
if devices_start >= 0:
    print(content[devices_start:devices_start+500])

# Fix the MCLH-08 friendly name (the garbled Russian text)
# The exact string is the friendly_name for 0x00158d0000d9cd2c
old_friendly_name = None
for line in content.split('\n'):
    if "0x00158d0000d9cd2c" in line:
        # Next line should have friendly_name
        continue
    if "friendly_name:" in line and old_friendly_name is None:
        # The previous line had 0x00158d0000d9cd2c, so this is the one to fix
        pass

# Simpler approach: find and replace by context
pattern = r"  '0x00158d0000d9cd2c':\n    friendly_name: .*"
replacement = "  '0x00158d0000d9cd2c':\n    friendly_name: datchik_kachestva_vozdukha"

new_content = re.sub(pattern, replacement, content, count=1)

if new_content != content:
    with sftp.open(remote_path, 'w') as f:
        f.write(new_content.encode('utf-8'))
    print("configuration.yaml updated!")
else:
    print("No changes made - pattern didn't match")

# Verify
print("\n=== Updated configuration.yaml ===")
with sftp.open(remote_path, 'r') as f:
    content = f.read().decode('utf-8')
devices_start = content.find('devices:')
if devices_start >= 0:
    print(content[devices_start:devices_start+500])

sftp.close()

# Restart Z2M
print("\n=== Restarting Zigbee2MQTT ===")
stdin, stdout, stderr = ssh.exec_command('docker restart big-bear-zigbee2mqtt', timeout=30)
print(stdout.read().decode('utf-8', errors='replace').strip())

import time
time.sleep(15)

# Check device info after restart
print("\n=== Device info after restart ===")
stdin2, stdout2, stderr2 = ssh.exec_command(
    'mosquitto_sub -h localhost -p 1883 -u mqtt -P CHANGE_ME '
    '-t zigbee2mqtt/bridge/devices -C 1 -W 5 -v 2>&1',
    timeout=10)
devices = stdout2.read().decode('utf-8', errors='replace').strip()
mclh_idx = devices.find("0x00158d0000d9cd2c")
if mclh_idx >= 0:
    start = devices.rfind("{", 0, mclh_idx)
    end = devices.find("}", mclh_idx)
    print(f"Device info: {devices[start:end+1]}")
else:
    print("Could not find MCLH-08 in devices list")

ssh.close()
