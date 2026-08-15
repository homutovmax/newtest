import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

# Check journalctl at 10:00
stdin, stdout, stderr = ssh.exec_command('journalctl -u cron --no-pager -S "2026-06-28 09:55:00" -U "2026-06-28 10:15:00" 2>&1')
print('=== JOURNAL 10:00 ===')
print(stdout.read().decode('utf-8', errors='replace'))

# Check log file again
stdin, stdout, stderr = ssh.exec_command('cat /var/log/hr-pipeline.log 2>&1')
print('=== PIPELINE LOG ===')
content = stdout.read().decode('utf-8', errors='replace')
print(content if content else '(empty)')

# Check if script has execute issue
stdin, stdout, stderr = ssh.exec_command('bash -n /opt/hr/run_pipeline.sh 2>&1; echo EXIT:$?')
print('=== SCRIPT CHECK ===')
print(stdout.read().decode('utf-8', errors='replace'))

# Check if container has python
stdin, stdout, stderr = ssh.exec_command('docker exec hr-web-1 python --version 2>&1')
print('=== PYTHON IN CONTAINER ===')
print(stdout.read().decode('utf-8', errors='replace'))

# Check if container has .env
stdin, stdout, stderr = ssh.exec_command('docker exec hr-web-1 sh -c "cat /app/.env 2>&1 | head -3"')
print('=== .env IN CONTAINER ===')
print(stdout.read().decode('utf-8', errors='replace'))

ssh.close()
