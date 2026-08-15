import paramiko, json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

# Get all entity IDs via HA API, save as JSON file on server
cmds = [
    """docker exec homeassistant python3 -c "
import json, urllib.request
TOKEN='CHANGE_ME'
h = {'Authorization': f'Bearer {TOKEN}'}
req = urllib.request.Request('http://localhost:8123/api/states', headers=h)
states = json.load(urllib.request.urlopen(req, timeout=15))
result = []
for s in states:
    eid = s['entity_id']
    name = s.get('attributes',{}).get('friendly_name','')
    if 'yandex' in eid or 'yndx' in eid or 'yandex' in name.lower() or 'yndx' in name.lower() or 'station' in eid:
        result.append({'entity_id': eid, 'state': s['state'], 'name': name, 'attrs': {k:v for k,v in s.get('attributes',{}).items() if k not in ('supported_features',)}})
# also dump all media_player
for s in states:
    if 'media_player' in s['entity_id']:
        name = s.get('attributes',{}).get('friendly_name','')
        result.append({'entity_id': s['entity_id'], 'state': s['state'], 'name': name})
print(json.dumps(result, ensure_ascii=False, indent=2))
" """
]

for cmd in cmds:
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    print(out)
    if err.strip():
        print("STDERR:", err)

ssh.close()
