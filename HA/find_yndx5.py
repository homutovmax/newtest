import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

cmd = """docker exec homeassistant python3 -c "
import json, urllib.request, os
TOKEN='CHANGE_ME'
h = {'Authorization': f'Bearer {TOKEN}'}

# Get device list
req = urllib.request.Request('http://localhost:8123/api/config/device_registry/list', headers=h)
devices = json.load(urllib.request.urlopen(req, timeout=15))

# Get states
req2 = urllib.request.Request('http://localhost:8123/api/states', headers=h)
states = json.load(urllib.request.urlopen(req2, timeout=15))

# Find all yandex related
lines = []
lines.append('=== YANDEX DEVICES ===')
for d in devices:
    name = d.get('name','') or ''
    ids = str(d.get('identifiers',[]))
    manuf = d.get('manufacturer','') or ''
    model = d.get('model','') or ''
    if any(x in (name+ids+manuf+model).lower() for x in ['yandex','station','yndx','alice']):
        lines.append(f'Device: {name}')
        lines.append(f'  id: {d.get("id","")}')
        lines.append(f'  identifiers: {ids}')
        lines.append(f'  model: {model}')
        lines.append(f'  manufacturer: {manuf}')
        # find entities for this device
        for s in states:
            ed = s.get('attributes',{}).get('device_id','')
            if ed == d.get('id',''):
                lines.append(f'  entity: {s[\"entity_id\"]} = {s[\"state\"]} name={s.get(\"attributes\",{}).get(\"friendly_name\",\"\")}')

lines.append('')
lines.append('=== ALL MEDIA_PLAYERS ===')
for s in states:
    if 'media_player' in s['entity_id']:
        a = s.get('attributes',{})
        lines.append(f'{s[\"entity_id\"]} | state={s[\"state\"]} | name={a.get(\"friendly_name\",\"\")}')

with open('/tmp/find.txt', 'w', encoding='utf-8') as f:
    f.write(chr(10).join(lines))
print('done')
" """

stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
print(stdout.read().decode())
err = stderr.read().decode()
if err: print("ERR:", err)

# docker cp out
ssh.exec_command("docker cp homeassistant:/tmp/find.txt /tmp/find.txt", timeout=15)
import time; time.sleep(2)

sftp = ssh.open_sftp()
sftp.get('/tmp/find.txt', 'C:\\NEWTEST\\HA\\find_result.txt')
sftp.close()

with open('C:\\NEWTEST\\HA\\find_result.txt', 'r', encoding='utf-8') as f:
    print(f.read())

ssh.close()
