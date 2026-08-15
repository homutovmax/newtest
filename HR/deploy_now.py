"""Deploy latest local files to server via paramiko SFTP."""
import paramiko, os, sys

LOCAL = r'C:\NEWTEST\HR'
SERVER = '192.168.1.92'
REMOTE = '/opt/hr'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(SERVER, username='root', password='CHANGE_ME', timeout=10)
sftp = ssh.open_sftp()

files_to_upload = []

# collect src/
for root, dirs, files in os.walk(os.path.join(LOCAL, 'src')):
    for f in files:
        if f.endswith('.pyc') or '__pycache__' in root:
            continue
        local = os.path.join(root, f)
        rel = os.path.relpath(local, LOCAL)
        remote = os.path.join(REMOTE, rel).replace('\\', '/')
        files_to_upload.append((local, remote))

# collect web/
for root, dirs, files in os.walk(os.path.join(LOCAL, 'web')):
    for f in files:
        if f.endswith('.pyc') or '__pycache__' in root:
            continue
        local = os.path.join(root, f)
        rel = os.path.relpath(local, LOCAL)
        remote = os.path.join(REMOTE, rel).replace('\\', '/')
        files_to_upload.append((local, remote))

# config files
config_files = [
    'run_pipeline.sh', 'send_report.sh', 'docker-compose.yml',
    'Dockerfile', 'requirements.txt', '.env.example',
]
for cf in config_files:
    local = os.path.join(LOCAL, cf)
    remote = os.path.join(REMOTE, cf).replace('\\', '/')
    if os.path.exists(local):
        files_to_upload.append((local, remote))

# migrations/
for root, dirs, files in os.walk(os.path.join(LOCAL, 'migrations')):
    for f in files:
        if f.endswith('.pyc') or '__pycache__' in root:
            continue
        local = os.path.join(root, f)
        rel = os.path.relpath(local, LOCAL)
        remote = os.path.join(REMOTE, rel).replace('\\', '/')
        files_to_upload.append((local, remote))

print(f"Uploading {len(files_to_upload)} files...")
for local, remote in files_to_upload:
    try:
        # Ensure remote directory exists
        rdir = os.path.dirname(remote)
        try:
            sftp.stat(rdir)
        except FileNotFoundError:
            parts = rdir.split('/')
            path = ''
            for p in parts:
                path += '/' + p
                try:
                    sftp.stat(path)
                except FileNotFoundError:
                    sftp.mkdir(path)

        sftp.put(local, remote)
        print(f'  {os.path.basename(local)}')
    except Exception as e:
        print(f'  FAIL {local}: {e}')

sftp.close()

# Restart container + run migration
print('\n=== Restarting web container ===')
stdin, stdout, stderr = ssh.exec_command('cd /opt/hr && docker compose restart web 2>&1')
print(stdout.read().decode('utf-8', errors='replace'))

print('=== Running migration ===')
stdin, stdout, stderr = ssh.exec_command('docker exec hr-web-1 alembic upgrade head 2>&1')
print(stdout.read().decode('utf-8', errors='replace'))

ssh.close()
print('=== Deploy complete ===')
