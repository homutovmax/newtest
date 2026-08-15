import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)
sftp = ssh.open_sftp()

# Upload fixed files
sftp.put(r'C:\NEWTEST\HR\src\models.py', '/opt/hr/src/models.py')
print('models.py uploaded')

sftp.put(r'C:\NEWTEST\HR\migrations\versions\001_create_vacancies.py', '/opt/hr/migrations/versions/001_create_vacancies.py')
print('001_create_vacancies.py uploaded')

sftp.put(r'C:\NEWTEST\HR\migrations\versions\004_enlarge_source_column.py', '/opt/hr/migrations/versions/004_enlarge_source_column.py')
print('004_enlarge_source_column.py uploaded')

sftp.close()

# Apply migration
print('\n=== Running migration ===')
stdin, stdout, stderr = ssh.exec_command('docker exec hr-web-1 alembic upgrade head 2>&1')
out = stdout.read().decode('utf-8', errors='replace')
print(out)

# Check migration status
print('=== Migration history ===')
stdin, stdout, stderr = ssh.exec_command('docker exec hr-web-1 alembic history 2>&1')
print(stdout.read().decode('utf-8', errors='replace'))

# Verify column type
print('=== Verify column type ===')
stdin, stdout, stderr = ssh.exec_command("""docker exec hr-web-1 python -c "
from src.database import SessionLocal
from sqlalchemy import inspect
s = SessionLocal()
insp = inspect(s.get_bind())
cols = insp.get_columns('vacancies')
for c in cols:
    if c['name'] == 'source':
        print(f'source: {c[\"type\"]}')
s.close()
" 2>&1""")
print(stdout.read().decode('utf-8', errors='replace'))

ssh.close()
