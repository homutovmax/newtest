import paramiko

HOST = '192.168.1.92'
USER = 'root'
PASS = 'CHANGE_ME'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=10)
sftp = ssh.open_sftp()

# Read current automations.yaml
with sftp.open('/DATA/AppData/homeassistant/config/automations.yaml', 'r') as f:
    content = f.read().decode('utf-8')

print("=== Current automations.yaml ===")
print(content)

sftp.close()
ssh.close()
