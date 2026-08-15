import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

cmd = """docker exec homeassistant python3 -c "
import json, urllib.request
TOKEN='CHANGE_ME'
h = {'Authorization': f'Bearer {TOKEN}'}
req = urllib.request.Request('http://localhost:8123/api/states', headers=h)
states = json.load(urllib.request.urlopen(req, timeout=15))
lines = []
for s in states:
    eid = s['entity_id']
    name = s.get('attributes',{}).get('friendly_name','')
    if 'media_player' in eid:
        lines.append(eid + ' | ' + s['state'] + ' | ' + name)
with open('/config/find.txt', 'w') as f:
    f.write(chr(10).join(lines))
print('done')
" """

stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
print("OUT:", stdout.read().decode())
print("ERR:", stderr.read().decode())

import time; time.sleep(2)

ssh.exec_command("docker cp homeassistant:/config/find.txt /tmp/find.txt", timeout=15)
time.sleep(2)

sftp = ssh.open_sftp()
sftp.get('/tmp/find.txt', 'C:\\NEWTEST\\HA\\find_result.txt')
sftp.close()

with open('C:\\NEWTEST\\HA\\find_result.txt', 'r', encoding='utf-8') as f:
    print(f.read())

ssh.close()
