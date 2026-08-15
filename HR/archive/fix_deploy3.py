import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=15)

def run(cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if out: print(out)
    if err: print('ERR:', err)
    return out, err, code

# Upload fixed files
import os
BASE = r'C:\NEWTEST\HR'
sftp = ssh.open_sftp()
for f in ['migrations/env.py', 'alembic.ini', 'src/config.py']:
    sftp.put(os.path.join(BASE, f), '/opt/hr/' + f.replace('\\', '/'), confirm=False)
    print(f'Uploaded {f}')
sftp.close()

# Rebuild and run debug first
out, err, code = run('cd /opt/hr && docker compose up -d --build web 2>&1')
print('Rebuild code=%d' % code)

import time
time.sleep(5)

# Check env vars inside container
out, err, code = run('docker exec hr-web-1 env | grep DB_URL')
print('DB_URL:', out)

if 'DB_URL' in out:
    # Check if it's really the issue
    out, err, code = run('docker exec hr-web-1 python -c "from src.config import settings; print(settings.db_url)"')
    print('From config:', out)

ssh.close()
