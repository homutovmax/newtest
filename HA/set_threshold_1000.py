import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)
sftp = ssh.open_sftp()

with sftp.open('/DATA/AppData/homeassistant/config/automations.yaml', 'r') as f:
    content = f.read().decode('utf-8')

content = content.replace('above: 600', 'above: 1000')

with sftp.open('/DATA/AppData/homeassistant/config/automations.yaml', 'w') as f:
    f.write(content.encode('utf-8'))

# Reload
import urllib.request, json
TOKEN = 'CHANGE_ME'
req = urllib.request.Request("http://192.168.1.92:8123/api/services/automation/reload",
    data=b'{}', headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}, method="POST")
urllib.request.urlopen(req, timeout=30)

sftp.close()
ssh.close()
print("Готово: триггер изменён на above: 1000")
