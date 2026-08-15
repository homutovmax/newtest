import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

# Clear old log for clean run
stdin, stdout, stderr = ssh.exec_command(': > /var/log/hr-pipeline.log; echo CLEARED')
print(stdout.read().decode('utf-8', errors='replace'))

print("=== RUNNING PIPELINE ===")
stdin, stdout, stderr = ssh.exec_command('bash /opt/hr/run_pipeline.sh 2>&1')
import time
start = time.time()
out = stdout.read().decode('utf-8', errors='replace')
elapsed = time.time() - start
print(f"=== DONE ({elapsed:.0f}s) ===")

# Check log
stdin, stdout, stderr = ssh.exec_command('cat /var/log/hr-pipeline.log')
log_content = stdout.read().decode('utf-8', errors='replace')
print("=== FULL LOG ===")
print(log_content)

# Check monitoring
stdin, stdout, stderr = ssh.exec_command("""docker exec hr-web-1 python -c "
from src.database import SessionLocal
from src.models import Vacancy, PipelineRun
from sqlalchemy import select, func
s = SessionLocal()
r = s.query(PipelineRun).order_by(PipelineRun.id.desc()).first()
total_v = s.query(Vacancy).count()
new_v = s.query(Vacancy).filter(Vacancy.status == 'new').count()
if r:
    print(f'Pipeline #{r.id}: status={r.status}, email={r.email_sent}, new_today={r.new_today}')
else:
    print('No runs found')
print(f'Vacancies: {total_v} total, {new_v} new')
s.close()
" 2>&1""")
print("\n=== MONITORING DB CHECK ===")
out = stdout.read().decode('utf-8', errors='replace')
print(out)

ssh.close()
