import paramiko, json, base64, time, re

HOST = '192.168.1.92'
USER = 'root'
PASS = 'CHANGE_ME'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=10)

stdin, stdout, stderr = ssh.exec_command(
    'mosquitto_sub -h localhost -p 1883 -u mqtt -P CHANGE_ME '
    '-t zigbee2mqtt/bridge/devices -C 1 -W 5 -v', timeout=15)
out = stdout.read().decode('utf-8', errors='replace')

match = re.search(r'"friendly_name":"([^"]+)"[^}]*?"ieee_address":"0x00158d0000d9cd2c"', out)
friendly = match.group(1) if match else "0x00158d0000d9cd2c"
print(f"Friendly name: {friendly}")

# Upload Python script to remote server
script_body = """
import subprocess, json, time, sys

def sub(t, to=15):
    r = subprocess.run(['mosquitto_sub','-h','localhost','-p','1883','-u','mqtt','-P','CHANGE_ME','-t',t,'-C','1','-W',str(to),'-v'], capture_output=True, text=True, timeout=to+5)
    return r.stdout.strip()

def pub(t, p):
    subprocess.run(['mosquitto_pub','-h','localhost','-p','1883','-u','mqtt','-P','CHANGE_ME','-t',t,'-m',json.dumps(p)])

friendly = sys.argv[1]
topic = "zigbee2mqtt/" + friendly
print("Waiting for device data...")
data = sub(topic, 120)
if data:
    print("Got:", data)
    print("Sending /get battery...")
    pub(topic + "/get", {"battery": ""})
    time.sleep(4)
    data2 = sub(topic, 10)
    print("After get:", data2 or "no response")
else:
    print("Timeout")
"""

with ssh.open_sftp() as sftp:
    with sftp.open('/tmp/get_battery_final.py', 'w') as f:
        f.write(script_body)
    # Write friendly name to file to avoid shell quoting issues
    with sftp.open('/tmp/mclh08_friendly.txt', 'w') as f:
        f.write(friendly)

cmd = 'python3 /tmp/get_battery_final.py "$(cat /tmp/mclh08_friendly.txt)"'
stdin, stdout, stderr = ssh.exec_command(cmd, timeout=180)
exit_code = stdout.channel.recv_exit_status()
out = stdout.read().decode('utf-8', errors='replace').strip()
err = stderr.read().decode('utf-8', errors='replace').strip()
for line in (out + '\n' + err).split('\n'):
    if line.strip():
        print(line.strip())
ssh.close()
