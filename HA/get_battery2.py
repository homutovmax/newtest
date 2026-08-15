import paramiko, json, re, uuid, time

HOST = '192.168.1.92'
USER = 'root'
PASS = 'CHANGE_ME'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=10)

# Get friendly name from bridge
stdin, stdout, stderr = ssh.exec_command(
    'mosquitto_sub -h localhost -p 1883 -u mqtt -P CHANGE_ME '
    '-t zigbee2mqtt/bridge/devices -C 1 -W 5 -v 2>&1', timeout=15)
out = stdout.read().decode('utf-8', errors='replace')

match = re.search(r'"friendly_name":"([^"]+)"[^}]*?"ieee_address":"0x00158d0000d9cd2c"', out)
if match:
    friendly = match.group(1)
    print(f"Friendly name: '{friendly}'")
else:
    friendly = "0x00158d0000d9cd2c"

# Upload script without format string issues
remote_script = '''
import subprocess, json, time, sys

def sub(topic, timeout=15):
    try:
        r = subprocess.run(
            ['mosquitto_sub', '-h', 'localhost', '-p', '1883',
             '-u', 'mqtt', '-P', 'CHANGE_ME',
             '-t', topic, '-C', '1', '-W', str(timeout), '-v'],
            capture_output=True, text=True, timeout=timeout+5)
        return r.stdout.strip()
    except:
        return None

def pub(topic, payload):
    subprocess.run(
        ['mosquitto_pub', '-h', 'localhost', '-p', '1883',
         '-u', 'mqtt', '-P', 'CHANGE_ME',
         '-t', topic, '-m', json.dumps(payload)],
        capture_output=True)

friendly = sys.argv[1]
print("Waiting for device to wake up (next report)...")
topic = "zigbee2mqtt/" + friendly
data = sub(topic, timeout=120)
if data:
    print("Device reported:", data)
    print("Requesting battery via /get...")
    pub(topic + "/get", {"battery": ""})
    time.sleep(3)
    data2 = sub(topic, timeout=10)
    if data2:
        print("After get:", data2)
    else:
        print("Waiting 5 more seconds...")
        time.sleep(5)
        data3 = sub(topic, timeout=10)
        if data3:
            print("After delay:", data3)
        else:
            print("Battery still not reported")
else:
    print("Device did not report within timeout")
'''

with ssh.open_sftp() as sftp:
    with sftp.open('/tmp/get_battery2.py', 'w') as f:
        f.write(remote_script)

# Need to pass friendly name with Russian chars safely
import base64
friendly_b64 = base64.b64encode(friendly.encode('utf-8')).decode()

cmd = f'python3 /tmp/get_battery2.py $(echo {friendly_b64} | base64 -d)'
stdin, stdout, stderr = ssh.exec_command(cmd, timeout=180)
exit_code = stdout.channel.recv_exit_status()
out = stdout.read().decode('utf-8', errors='replace').strip()
err = stderr.read().decode('utf-8', errors='replace').strip()
for line in (out + '\n' + err).split('\n'):
    if line.strip():
        print(line.strip())
ssh.close()
