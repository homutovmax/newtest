import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

stdin, stdout, stderr = ssh.exec_command('cat /var/log/cron.log 2>&1 | tail -30')
print('=== CRON.LOG ===')
print(stdout.read().decode('utf-8', errors='replace'))

# Check if cron daemon has debug logging
stdin, stdout, stderr = ssh.exec_command('cat /etc/default/cron 2>/dev/null; echo ==; cat /etc/rsyslog.d/50-default.conf 2>/dev/null | grep -i cron')
print('\n=== CRON CONFIG ===')
print(stdout.read().decode('utf-8', errors='replace'))

# Check the actual file modification time vs expected run times
stdin, stdout, stderr = ssh.exec_command('ls -la /var/log/hr-pipeline.log; echo ==; stat /var/log/hr-pipeline.log | grep -i modif')
print('\n=== LOG STAT ===')
print(stdout.read().decode('utf-8', errors='replace'))

# Run the script with timeout to catch any immediate errors
stdin, stdout, stderr = ssh.exec_command('timeout 5 bash /opt/hr/run_pipeline.sh 2>&1; echo "EXIT: $?"')
print('\n=== QUICK TEST (5s) ===')
out = stdout.read().decode('utf-8', errors='replace')
print(out if out else '(empty)')

ssh.close()
