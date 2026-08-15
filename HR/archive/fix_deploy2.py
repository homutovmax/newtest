import paramiko, os

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=15)
sftp = ssh.open_sftp()

BASE = r'C:\NEWTEST\HR'

def run(cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if out: print(out)
    if err: print('ERR:', err)
    return out, err, code

# Upload updated files
for f in ['src/config.py', 'docker-compose.yml']:
    local = os.path.join(BASE, f)
    remote = '/opt/hr/' + f.replace('\\', '/')
    sftp.put(local, remote, confirm=False)
    print(f'Uploaded {f}')

sftp.close()

# Fix .env  
run("""cat > /opt/hr/.env << 'EOF'
DB_URL=postgresql://hr:hr@db/hr
PUBLIC_URL=http://192.168.1.92:8000
LOG_LEVEL=INFO
EOF""")

# Rebuild and start
out, err, code = run('cd /opt/hr && docker compose up -d --build web 2>&1')
print('Rebuild code=%d' % code)

import time
time.sleep(5)

# Check status
out, err, code = run('docker exec hr-web-1 python -c "print(1)" 2>&1')
if code == 0:
    out, err, code = run('docker exec hr-web-1 alembic upgrade head 2>&1')
    print('Alembic:', code)

    out, err, code = run('docker exec hr-web-1 python -m src.migration 2>&1')
    print('Migration:', code)

    out, err, code = run('curl -s http://localhost:8000/health')
    print('Health:', out)
else:
    out, err, code = run('docker logs hr-web-1 2>&1 | tail -30')
    print('Container failed')

ssh.close()
print('=== DONE ===')
