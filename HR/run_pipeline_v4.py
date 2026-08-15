import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)
sftp = ssh.open_sftp()

# Upload the fixed generate_covers.py again (just in case)
sftp.put(r'C:\NEWTEST\HR\src\generate_covers.py', '/opt/hr/src/generate_covers.py')

# Clear log
stdin, stdout, stderr = ssh.exec_command(': > /var/log/hr-pipeline.log')
print(stdout.read().decode('utf-8', errors='replace'))

import time
print("=== RUNNING PIPELINE ===")
start = time.time()
stdin, stdout, stderr = ssh.exec_command('bash /opt/hr/run_pipeline.sh 2>&1')
out = stdout.read().decode('utf-8', errors='replace')
elapsed = time.time() - start
print(f"=== DONE ({elapsed:.0f}s) ===")

# Show LOG
stdin, stdout, stderr = ssh.exec_command("tail -40 /var/log/hr-pipeline.log")
log = stdout.read().decode('utf-8', errors='replace')
print("=== LOG (last 40 lines) ===")
print(log)

# DB check
stdin, stdout, stderr = ssh.exec_command("""docker exec hr-web-1 python -c "
from src.database import SessionLocal
from src.models import PipelineRun, Vacancy
s = SessionLocal()
r = s.query(PipelineRun).order_by(PipelineRun.id.desc()).first()
if r:
    print(f'Run #{r.id}: status={r.status}, email={r.email_sent}, new={r.new_today}, dur={r.duration_seconds}s, err={r.error_message}')
print(f'Vacancies: {s.query(Vacancy).count()} total, {s.query(Vacancy).filter(Vacancy.status==\"new\").count()} new')
s.close()
" 2>&1""")
print("\n=== DB CHECK ===")
print(stdout.read().decode('utf-8', errors='replace'))

sftp.close()
ssh.close()
