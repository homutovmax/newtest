import paramiko, json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)
sftp = ssh.open_sftp()

with sftp.open('/DATA/AppData/homeassistant/config/.storage/core.config_entries', 'r') as f:
    data = json.loads(f.read().decode('utf-8'))

print(json.dumps(data, indent=2)[:3000])

sftp.close()
ssh.close()
