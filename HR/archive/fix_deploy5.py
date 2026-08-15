import paramiko, time, os

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=15)

def run(cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if out: print(out)
    if err and code != 0: print('ERR:', err[:300])
    return code

sftp = ssh.open_sftp()
BASE = r'C:\NEWTEST\HR'
for f in ['src/models.py', 'src/migration.py', 'migrations/versions/002_company_text.py']:
    sftp.put(os.path.join(BASE, f), '/opt/hr/' + f.replace('\\', '/'), confirm=False)
    print(f'Uploaded {f}')
sftp.close()

print('Rebuilding web...')
code = run('cd /opt/hr && docker compose up -d --build web 2>&1')
print('Build:', 'OK' if code == 0 else f'FAIL ({code})')
time.sleep(5)

code = run('docker inspect -f {{.State.Status}} hr-web-1')
print('Container:', code)

print('Running alembic upgrade...')
code = run('docker exec hr-web-1 alembic upgrade head 2>&1')
print('Alembic:', 'OK' if code == 0 else f'FAIL ({code})')

print('Running data migration...')
code = run('docker exec hr-web-1 python -m src.migration 2>&1')
print('Migration:', 'OK' if code == 0 else f'FAIL ({code})')

import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(5)
try:
    s.connect(('192.168.1.92', 8000))
    s.send(b'GET /health HTTP/1.0\r\n\r\n')
    resp = s.recv(4096).decode()
    print('Web health:', resp.split('\r\n')[-1].strip() if resp else 'no response')
except Exception as e:
    print('Web not reachable:', e)
finally:
    s.close()

ssh.close()
print('=== DONE ===')
