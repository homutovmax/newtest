import paramiko, json

HOST = '192.168.1.92'
USER = 'root'
PASS = 'CHANGE_ME'
TOKEN = 'CHANGE_ME'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=10)

# Upload a Python check script
script = '''import json, urllib.request
req = urllib.request.Request("http://localhost:8123/api/states",
    headers={"Authorization": "Bearer ''' + TOKEN + '''", "Content-Type": "application/json"})
data = json.load(urllib.request.urlopen(req))
for s in data:
    if "00158d0000d9cd2c" in s["entity_id"]:
        print(s["entity_id"], "=", s["state"])
if not any("00158d0000d9cd2c" in s["entity_id"] for s in data):
    print("No MCLH-08 entities found in HA")
    # Print all sensor entities for debugging
    for s in data:
        if "sensor." in s["entity_id"]:
            print("  other:", s["entity_id"], "=", s.get("state", "?"))
'''

with ssh.open_sftp() as sftp:
    with sftp.open('/tmp/check_ha.py', 'w') as f:
        f.write(script)

stdin, stdout, stderr = ssh.exec_command('python3 /tmp/check_ha.py', timeout=20)
exit_code = stdout.channel.recv_exit_status()
out = stdout.read().decode('utf-8', errors='replace').strip()
err = stderr.read().decode('utf-8', errors='replace').strip()
print(out if out else err)
ssh.close()
