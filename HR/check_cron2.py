import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

# Check if there's mail for root about cron errors
stdin, stdout, stderr = ssh.exec_command('ls -la /var/mail/ /var/spool/mail/ 2>&1; echo ===; cat /var/mail/root 2>/dev/null | tail -30; echo ===; cat /var/spool/mail/root 2>/dev/null | tail -30')
print('=== MAIL ===')
print(stdout.read().decode('utf-8', errors='replace'))

# Check all cron entries for today
stdin, stdout, stderr = ssh.exec_command('journalctl -u cron --no-pager -S today 2>&1 | grep -i "hr\|pipeline\|send_report\|run_pipeline"')
print('=== CRON HR ENTRIES TODAY ===')
out = stdout.read().decode('utf-8', errors='replace')
print(out if out else '(none found)')

# Check if maybe the issue is that the script doesn't have correct path
stdin, stdout, stderr = ssh.exec_command('head -1 /opt/hr/run_pipeline.sh; which bash; ls -la /opt/hr/')
print('=== SCRIPT HEAD ===')
print(stdout.read().decode('utf-8', errors='replace'))

# Check if cron has any errors in syslog
stdin, stdout, stderr = ssh.exec_command('grep -i "cron\|pipeline\|send_report" /var/log/syslog 2>/dev/null | tail -20')
print('=== SYSLOG ===')
out = stdout.read().decode('utf-8', errors='replace')
print(out if out else '(none found)')

# Restart cron to be safe
stdin, stdout, stderr = ssh.exec_command('systemctl restart cron 2>&1; echo "RESTART: $?"')
print('=== CRON RESTART ===')
print(stdout.read().decode('utf-8', errors='replace'))

ssh.close()
