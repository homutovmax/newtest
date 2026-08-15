import paramiko, os

BASE = r'C:\NEWTEST\HR'
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=15)
sftp = ssh.open_sftp()

# Upload fixed config.py
local = os.path.join(BASE, 'src', 'config.py')
remote = '/opt/hr/src/config.py'
sftp.put(local, remote, confirm=False)
print('config.py uploaded')

# Fix .env
def run(cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if out: print(out)
    if err: print('ERR:', err)
    return out, err, code

import time

out, err, code = run("""cat > /opt/hr/.env << 'EOF'
DB_URL=postgresql://hr:hr@db/hr
PUBLIC_URL=http://192.168.1.92:8000
LOG_LEVEL=INFO
EOF""")
print('.env written (code=%d)' % code)

# Rebuild web container
out, err, code = run('cd /opt/hr && docker compose up -d --build web 2>&1')
print('docker compose done (code=%d)' % code)

# Wait and check
time.sleep(5)

out, err, code = run('docker ps --filter name=hr-web --format "{{.Status}}" 2>&1')
print('Web status check (code=%d)' % code)

# Check if container is running
out, err, code2 = run('docker exec hr-web-1 python -c "print(1)" 2>&1')
if code2 == 0:
    print('Running migration...')
    out, err, code = run('docker exec hr-web-1 alembic upgrade head 2>&1')
    print('Alembic:', 'OK' if code == 0 else 'FAIL')

    out, err, code = run('docker exec hr-web-1 python -m src.migration 2>&1')
    print('Migration:', 'OK' if code == 0 else 'FAIL')

    out, err, code = run('curl -s http://localhost:8000/health 2>&1')
    print('Health:', 'OK' if code == 0 else 'FAIL')
else:
    print('Web container failed to start')
    out, err, code = run('docker logs hr-web-1 2>&1 | tail -20')
sftp.close()
ssh.close()
print('=== DONE ===')
