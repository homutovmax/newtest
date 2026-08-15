import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)
sftp = ssh.open_sftp()

# Upload the local version of update_vacancies.py
local_path = r'C:\NEWTEST\HR\update_vacancies.py'
sftp.put(local_path, '/opt/hr/update_vacancies.py')
print('update_vacancies.py uploaded')

# Also upload generate_covers.py and report.py
sftp.put(r'C:\NEWTEST\HR\src\generate_covers.py', '/opt/hr/src/generate_covers.py')
sftp.put(r'C:\NEWTEST\HR\src\report.py', '/opt/hr/src/report.py')
print('src/generate_covers.py uploaded')
print('src/report.py uploaded')

# Check syntax inside the container
stdin, stdout, stderr = ssh.exec_command("docker exec hr-web-1 python -c \"import py_compile; py_compile.compile('/app/update_vacancies.py', doraise=True); print('SYNTAX OK')\" 2>&1")
print('\n=== SYNTAX CHECK ===')
print(stdout.read().decode('utf-8', errors='replace'))

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

# Show LOG (last 30 lines)
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
    if r.error_message:
        print(f'ERROR: {r.error_message[:200]}')
print(f'Vacancies: {s.query(Vacancy).count()} total, {s.query(Vacancy).filter(Vacancy.status==\"new\").count()} new')
s.close()
" 2>&1""")
print("\n=== DB CHECK ===")
print(stdout.read().decode('utf-8', errors='replace'))

sftp.close()
ssh.close()
