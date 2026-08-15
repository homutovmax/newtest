import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

# Run inside docker, save to file with utf-8
cmd = """docker exec homeassistant python3 -c "
import json, urllib.request
TOKEN='CHANGE_ME'
h = {'Authorization': f'Bearer {TOKEN}'}
req = urllib.request.Request('http://localhost:8123/api/states', headers=h)
states = json.load(urllib.request.urlopen(req, timeout=15))
result = []
for s in states:
    eid = s['entity_id']
    name = s.get('attributes',{}).get('friendly_name','')
    if 'yandex' in eid or 'yndx' in eid.lower() or 'yandex' in name.lower() or 'station' in eid or 'media_player' in eid:
        result.append({'id': eid, 'state': s['state'], 'name': name})
with open('/tmp/entities.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print('saved')
" """

stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

# Now copy file out
sftp = ssh.open_sftp()
sftp.get('/tmp/entities.json', 'C:\\NEWTEST\\HA\\entities.json')
sftp.close()

# Read with UTF-8
with open('C:\\NEWTEST\\HA\\entities.json', 'r', encoding='utf-8') as f:
    print(f.read())

ssh.close()
