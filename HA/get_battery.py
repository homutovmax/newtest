import paramiko, json, uuid, time

HOST = '192.168.1.92'
USER = 'root'
PASS = 'CHANGE_ME'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=10)

# First, find the friendly name of the MCLH-08 device
stdin, stdout, stderr = ssh.exec_command(
    'mosquitto_sub -h localhost -p 1883 -u mqtt -P CHANGE_ME '
    '-t zigbee2mqtt/bridge/devices -C 1 -W 5 -v 2>&1', timeout=15)
out = stdout.read().decode('utf-8', errors='replace')

import re
match = re.search(r'"friendly_name":"([^"]+)"[^}]*?"model":"MCLH-08"', out)
if not match:
    # Try broader search
    match = re.search(r'"friendly_name":"([^"]+)"[^}]*?"ieee_address":"0x00158d0000d9cd2c"', out)

if match:
    friendly = match.group(1)
    print(f"Friendly name: '{friendly}'")
else:
    print("Could not find MCLH-08 friendly name, using ieee address")
    friendly = "0x00158d0000d9cd2c"

# Subscribe to device topic to detect wakeup
wakeup_script = f'''
import json, subprocess, time

def sub(topic, timeout=15):
    try:
        result = subprocess.run(
            ['mosquitto_sub', '-h', 'localhost', '-p', '1883', '-u', 'mqtt',
             '-P', 'CHANGE_ME', '-t', topic, '-C', '1', '-W', str(timeout), '-v'],
            capture_output=True, text=True, timeout=timeout+5)
        return result.stdout.strip()
    except:
        return None

def pub(topic, payload):
    subprocess.run(
        ['mosquitto_pub', '-h', 'localhost', '-p', '1883', '-u', 'mqtt',
         '-P', 'CHANGE_ME', '-t', topic, '-m', json.dumps(payload)],
        capture_output=True)

print("Waiting for device to wake up...")
data = sub("zigbee2mqtt/{friendly}", timeout=120)
if data:
    print(f"Device reported: {{data}}")
    print("Sending /get for battery...")
    pub("zigbee2mqtt/{friendly}/get", {{"battery": ""}})
    time.sleep(3)
    
    # Try to get updated data
    data2 = sub("zigbee2mqtt/{friendly}", timeout=10)
    if data2:
        print(f"After get: {{data2}}")
    else:
        print("No immediate response, checking one more time...")
        time.sleep(5)
        data3 = sub("zigbee2mqtt/{friendly}", timeout=10)
        if data3:
            print(f"After delay: {{data3}}")
        else:
            print("Battery value did not update")
else:
    print("Device did not report within timeout")
'''

# Write the script to server
script_content = wakeup_script.format(friendly=friendly)
with ssh.open_sftp() as sftp:
    with sftp.open('/tmp/get_battery.py', 'w') as f:
        f.write(script_content)

stdin, stdout, stderr = ssh.exec_command('python3 /tmp/get_battery.py', timeout=180)
exit_code = stdout.channel.recv_exit_status()
out = stdout.read().decode('utf-8', errors='replace').strip()
err = stderr.read().decode('utf-8', errors='replace').strip()
for line in (out + '\n' + err).split('\n'):
    if line.strip():
        print(line.strip())
ssh.close()
