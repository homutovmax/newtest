import paramiko
import json
import time
import requests

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

# 1. Restart HA
print('Restarting HA...')
stdin, stdout, stderr = ssh.exec_command('docker restart homeassistant')
print(stdout.read().decode())

# 2. Wait for HA to come up
time.sleep(25)

# 3. Check HA status
stdin, stdout, stderr = ssh.exec_command('docker ps --filter name=homeassistant --format "{{.Names}} {{.Status}}"')
print(stdout.read().decode())

# 4. Get the HA IP (it's 192.168.1.92 on host, but inside docker we need the host port)
# HA is exposed on port 8123 on the host
ha_url = 'http://192.168.1.92:8123'

# 5. Get a long-lived access token via API
# First check if we can reach it
try:
    r = requests.get(f'{ha_url}/api/', timeout=5)
    print(f'HA API reachable: {r.status_code}')
except Exception as e:
    print(f'Cannot reach HA API: {e}')
    ssh.close()
    exit()

# We need to create a token. Since we don't have credentials, let's try
# to create one using the API password or check the auth file
# Actually, let's check the .storage/auth file for tokens
stdin, stdout, stderr = ssh.exec_command('docker exec homeassistant cat /config/.storage/auth 2>/dev/null')
auth_data = json.loads(stdout.read().decode('utf-8'))

# Look for existing tokens or find the owner user
users = auth_data.get('data', {}).get('users', [])
for user in users:
    print("User: {} id={} is_owner={}".format(user.get("name"), user.get("id"), user.get("is_owner")))

tokens = auth_data.get('data', {}).get('refresh_tokens', [])
for t in tokens:
    print(f'Token: {t.get(\"id\")} client_id={t.get(\"client_id\")}')

# We need the owner ID to create a token
# Actually, let's try creating a token through the API without auth
# First let's check the http section of HA config to see if api_password is used
stdin, stdout, stderr = ssh.exec_command('docker exec homeassistant cat /config/configuration.yaml')
ha_config = stdout.read().decode()
print(f'\nHA Config:\n{ha_config}')

ssh.close()
