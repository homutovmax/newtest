import paramiko
import json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)
sftp = ssh.open_sftp()

# 1. Read HA config
with sftp.open('/DATA/AppData/homeassistant/config/configuration.yaml', 'r') as f:
    content = f.read().decode('utf-8')

print('=== BEFORE ===')
print(content)

# 2. Remove mqtt block
lines = content.split('\n')
result = []
in_mqtt = False
for line in lines:
    if line.startswith('mqtt:'):
        in_mqtt = True
        continue
    if in_mqtt:
        if line.strip() == '' or not line.startswith(' '):
            in_mqtt = False
            if line.strip() != '':
                result.append(line)
        continue
    result.append(line)

new_content = '\n'.join(result)

print('=== AFTER ===')
print(new_content)

# 3. Write back
with sftp.open('/DATA/AppData/homeassistant/config/configuration.yaml', 'w') as f:
    f.write(new_content.encode('utf-8'))

sftp.close()
ssh.close()
print('Config updated successfully')
