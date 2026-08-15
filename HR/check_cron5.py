import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

# Check syslog for cron errors at 10:00
stdin, stdout, stderr = ssh.exec_command("grep -i 'cron.*FAIL\|cron.*error\|cron.*not found' /var/log/syslog 2>/dev/null | tail -10")
print('=== SYSLOG CRON ERRORS ===')
out = stdout.read().decode('utf-8', errors='replace')
print(out if out else '(none)')

# Check if /bin/bash exists
stdin, stdout, stderr = ssh.exec_command("ls -la /bin/bash /usr/bin/bash 2>&1")
print('\n=== BASH LOCATION ===')
print(stdout.read().decode('utf-8', errors='replace'))

# Test with cron-like minimal environment
stdin, stdout, stderr = ssh.exec_command("env -i HOME=/root LOGNAME=root SHELL=/bin/sh PATH=/usr/bin:/bin /opt/hr/run_pipeline.sh 2>&1 & PID=$!; sleep 3; kill $PID 2>/dev/null; wait $PID 2>/dev/null; echo '---'; cat /var/log/hr-pipeline.log | tail -3")
print('\n=== CRON-LIKE EXECUTION TEST ===')
out = stdout.read().decode('utf-8', errors='replace')
print(out if out else '(empty)')

# Check cron debug - look for when it last read crontab
stdin, stdout, stderr = ssh.exec_command("grep -i 'cron.*reload\|cron.*crontab\|cron.*root' /var/log/syslog 2>/dev/null | tail -5")
print('\n=== CRON RELOAD EVENTS ===')
out = stdout.read().decode('utf-8', errors='replace')
print(out if out else '(none)')

ssh.close()
