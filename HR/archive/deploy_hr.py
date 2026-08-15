#!/usr/bin/env python3
"""Deploy HR 2.0 to 192.168.1.92 via SSH + Docker."""
import paramiko, os, sys, time

HOST = '192.168.1.92'
USER = 'root'
PASS = 'CHANGE_ME'
PROJECT = '/opt/hr'
BASE = os.path.dirname(os.path.abspath(__file__))

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=15)

def run(cmd, check=True):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    exit_code = stdout.channel.recv_exit_status()
    out = stdout.read().decode('utf-8').strip()
    err = stderr.read().decode('utf-8').strip()
    if out: print(out)
    if err: print(err, file=sys.stderr)
    if check and exit_code != 0:
        raise RuntimeError(f'Command failed: {cmd}')
    return out, err, exit_code

# 1. Check Docker
print('=== 1. Checking Docker ===')
run('docker --version')
run('docker compose version')

# 2. Create project directory
print('=== 2. Creating project directory ===')
run(f'mkdir -p {PROJECT}')

# 3. SFTP project files (exclude archive, __pycache__, .git, etc.)
print('=== 3. Uploading project files ===')
sftp = ssh.open_sftp()

EXCLUDE = {'.git', '__pycache__', '.pytest_cache', '.env', 'node_modules', 'archive', 'ansible', 'cover_v', 'vacancies_history.json'}

def upload_dir(local, remote):
    for root, dirs, files in os.walk(local):
        # Skip excluded
        rel = os.path.relpath(root, local)
        if rel == '.':
            rel = ''
        parts = rel.split(os.sep) if rel else []
        skip = False
        for p in parts:
            if p in EXCLUDE or any(e in p for e in EXCLUDE):
                skip = True
                break
        if skip:
            continue
        # Create remote dir
        remote_dir = os.path.join(remote, rel).replace('\\', '/')
        try:
            sftp.stat(remote_dir)
        except FileNotFoundError:
            sftp.mkdir(remote_dir)
        # Upload files
        for f in files:
            if f.endswith('.pyc') or f in EXCLUDE or f.startswith('cover_v') or f == 'vacancies_history.json':
                continue
            local_path = os.path.join(root, f)
            remote_path = os.path.join(remote_dir, f).replace('\\', '/')
            try:
                sftp.stat(remote_path)
                # Skip if same size (optimization)
                local_size = os.path.getsize(local_path)
                remote_size = sftp.stat(remote_path).st_size
                if local_size == remote_size:
                    continue
            except FileNotFoundError:
                pass
            sftp.put(local_path, remote_path, confirm=False)

upload_dir(BASE, PROJECT)
sftp.close()
print('Upload complete')

# 4. Create .env
print('=== 4. Creating .env ===')
run(f"""cat > {PROJECT}/.env << 'ENVEOF'
DB_URL=postgresql://hr:hr@db/hr
DB_PASSWORD=hr
PUBLIC_URL=http://192.168.1.92:8000
LOG_LEVEL=INFO
ENVEOF""")

# 5. Docker compose up
print('=== 5. Starting Docker Compose ===')
run(f'cd {PROJECT} && docker compose up -d --build')

# 6. Wait for DB
print('=== 6. Waiting for PostgreSQL ===')
for i in range(30):
    _, _, code = run(f'docker compose -f {PROJECT}/docker-compose.yml exec -T db pg_isready -U hr', check=False)
    if code == 0:
        print('PostgreSQL is ready')
        break
    time.sleep(2)

# 7. Run migration
print('=== 7. Running migration ===')
# Copy history file to server
sftp2 = ssh.open_sftp()
loc_hist = os.path.join(BASE, 'vacancies_history.json')
rem_hist = f'{PROJECT}/vacancies_history.json'
try:
    sftp2.stat(rem_hist)
except FileNotFoundError:
    sftp2.put(loc_hist, rem_hist, confirm=False)
    print('History file uploaded')
sftp2.close()

# Run migration inside container
run(f'docker compose -f {PROJECT}/docker-compose.yml exec -T web alembic upgrade head')
run(f'docker compose -f {PROJECT}/docker-compose.yml exec -T web python -m src.migration')

# 8. Verify
print('=== 8. Verifying ===')
out, _, _ = run('curl -s http://localhost:8000/health')
print(f'Health check: {out}')

ssh.close()
print('=== DEPLOY COMPLETE ===')
print(f'Web: http://192.168.1.92:8000/report')
