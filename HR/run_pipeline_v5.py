import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)
sftp = ssh.open_sftp()

# Read file
with sftp.open('/opt/hr/update_vacancies.py', 'rb') as f:
    content = f.read().decode('utf-8')

# Fix the broken syntax: str(s or '') -> str(s or ''))
content = content.replace("html_mod.escape(str(s or '')", "html_mod.escape(str(s or ''))")
# Also fix vac_card: str(v.get("salary", ""))
content = content.replace("esc(str(v.get('salary', '')", "esc(str(v.get('salary', ''))")

with sftp.open('/opt/hr/update_vacancies.py', 'wb') as f:
    f.write(content.encode('utf-8'))

# Check syntax
stdin, stdout, stderr = ssh.exec_command('python -c "import py_compile; py_compile.compile(\'/opt/hr/update_vacancies.py\', doraise=True)" 2>&1')
print('Syntax check:', stdout.read().decode('utf-8', errors='replace') or 'OK')

# Upload local version of generate_covers.py again
sftp.put(r'C:\NEWTEST\HR\src\generate_covers.py', '/opt/hr/src/generate_covers.py')
print('generate_covers.py uploaded')

# Clear log
stdin, stdout, stderr = ssh.exec_command(': > /var/log/hr-pipeline.log; echo CLEARED')
print(stdout.read().decode('utf-8', errors='replace'))

import time
print("=== RUNNING PIPELINE ===")
start = time.time()
stdin, stdout, stderr = ssh.exec_command('bash /opt/hr/run_pipeline.sh 2>&1')
out = stdout.read().decode('utf-8', errors='replace')
elapsed = time.time() - start
print(f"=== DONE ({elapsed:.0f}s) ===")

# Show LOG (tail)
stdin, stdout, stderr = ssh.exec_command("tail -30 /var/log/hr-pipeline.log")
log = stdout.read().decode('utf-8', errors='replace')
print("=== LOG (last 30 lines) ===")
print(log)

# DB check
stdin, stdout, stderr = ssh.exec_command("""docker exec hr-web-1 python -c "
from src.database import SessionLocal
from src.models import PipelineRun, Vacancy
s = SessionLocal()
r = s.query(PipelineRun).order_by(PipelineRun.id.desc()).first()
if r:
    print(f'Run #{r.id}: status={r.status}, email={r.email_sent}, new_today={r.new_today}, dur={r.duration_seconds}s')
print(f'Vacancies: {s.query(Vacancy).count()} total, {s.query(Vacancy).filter(Vacancy.status==\"new\").count()} new')
s.close()
" 2>&1""")
print("\n=== DB CHECK ===")
print(stdout.read().decode('utf-8', errors='replace'))

sftp.close()
ssh.close()
