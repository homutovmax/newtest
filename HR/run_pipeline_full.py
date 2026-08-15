import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

# Clear old log for clean check
stdin, stdout, stderr = ssh.exec_command('cp /var/log/hr-pipeline.log /var/log/hr-pipeline.log.bak 2>/dev/null; : > /var/log/hr-pipeline.log; echo CLEARED')
print(stdout.read().decode('utf-8', errors='replace'))

print("=== START PIPELINE ===")
stdin, stdout, stderr = ssh.exec_command('bash /opt/hr/run_pipeline.sh 2>&1')
start = time.time()
out = stdout.read().decode('utf-8', errors='replace')
elapsed = time.time() - start

print(f"=== DONE ({elapsed:.0f}s) ===")
print(out[-3000:])
print(f"\n=== EXIT CODE CHECK ===")
print("SUCCESS" if "exit 0" in out or "done" in out.lower() else "CHECK LOG BELOW")

# Check the log
stdin, stdout, stderr = ssh.exec_command('wc -l /var/log/hr-pipeline.log; echo "---"; tail -20 /var/log/hr-pipeline.log')
print("\n=== LOG FILE ===")
print(stdout.read().decode('utf-8', errors='replace'))

# Verify email was sent by looking at pipeline_monitor
stdin, stdout, stderr = ssh.exec_command("""docker exec hr-web-1 python -c "
from src.database import SessionLocal
from src.models import PipelineRun
s = SessionLocal()
r = s.query(PipelineRun).order_by(PipelineRun.id.desc()).first()
if r: print(f'Run #{r.id}: status={r.status}, email_sent={r.email_sent}, error={r.error_message}')
else: print('No runs found')
s.close()
" 2>&1""")
print("\n=== MONITORING CHECK ===")
out = stdout.read().decode('utf-8', errors='replace')
print(out if out else '(empty)')

ssh.close()
