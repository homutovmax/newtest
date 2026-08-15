import paramiko, json

HOST = '192.168.1.92'
USER = 'root'
PASS = 'CHANGE_ME'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=10)

sftp = ssh.open_sftp()

# Read state.json to find the actual device name
print("=== Reading Z2M state.json ===")
with sftp.open('/DATA/AppData/big-bear-zigbee2mqtt/data/state.json', 'r') as f:
    state = json.loads(f.read().decode('utf-8'))

# Find MCLH-08 device
for key, value in state.items():
    if '00158d0000d9cd2c' in str(value) or '00158d0000d9cd2c' == key:
        print(f"Found: {key}")
        if isinstance(value, dict):
            print(json.dumps(value, indent=2, ensure_ascii=False)[:2000])

# Look at all device keys
print("\n=== All devices in state ===")
for key in state:
    if key.startswith('0x'):
        val = state[key]
        if isinstance(val, dict):
            fn = val.get('friendly_name', '?')
            print(f"  {key}: friendly_name='{fn}'")

# Try proper rename using the current friendly name from state
# First find the current friendly name
current_name = None
for key, value in state.items():
    if isinstance(value, dict) and value.get('ieee_address') == '0x00158d0000d9cd2c':
        current_name = value.get('friendly_name', '')
        break
    if key == '0x00158d0000d9cd2c':
        if isinstance(value, dict):
            current_name = value.get('friendly_name', '')

if current_name:
    print(f"\nCurrent friendly_name: '{current_name}'")
    print(f"Repr: {repr(current_name)}")
    
    # Rename via state.json modification
    print("\n=== Attempting rename via state.json ===")
    
    # Find and update the device in state.json
    for key in state:
        if isinstance(state[key], dict):
            if state[key].get('ieee_address') == '0x00158d0000d9cd2c':
                print(f"Updating key {key}")
                state[key]['friendly_name'] = 'datchik_kachestva_vozdukha'
                state[key]['model'] = 'Air quality sensor'
                state[key]['vendor'] = 'LifeControl'
                print(f"Updated: {json.dumps(state[key], indent=2, ensure_ascii=False)[:500]}")
            if key == '0x00158d0000d9cd2c':
                if isinstance(state[key], dict):
                    state[key]['friendly_name'] = 'datchik_kachestva_vozdukha'
                    print(f"Updated key 0x00158d0000d9cd2c")
    
    # Write updated state.json
    print("\n=== Writing updated state.json ===")
    with sftp.open('/DATA/AppData/big-bear-zigbee2mqtt/data/state.json', 'w') as f:
        f.write(json.dumps(state, indent=2, ensure_ascii=False).encode('utf-8'))
    print("state.json updated!")
else:
    print("Could not find current friendly name")

sftp.close()

# Restart Z2M to apply changes
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

ssh.close()
