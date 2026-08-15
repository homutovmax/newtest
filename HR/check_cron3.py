import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

# Check ALL cron entries today (full dump)
stdin, stdout, stderr = ssh.exec_command('journalctl -u cron --no-pager -S "2026-06-28 00:00:00" 2>&1')
print('=== ALL CRON TODAY ===')
out = stdout.read().decode('utf-8', errors='replace')
# Only show lines with CMD
for line in out.split('\n'):
    if 'CMD' in line or 'pipeline' in line.lower() or 'send_report' in line.lower() or 'hr' in line.lower():
        print(line)
if 'CMD' not in out:
    print("(no CMD lines found - showing all)")
    print(out[-2000:])

# Check if crontab is actually read by cron
stdin, stdout, stderr = ssh.exec_command('crontab -l 2>&1; echo "---"; ls -la /var/spool/cron/crontabs/ 2>&1')
print('\n=== CRONTAB ===')
print(stdout.read().decode('utf-8', errors='replace'))

# Check most recent log entries
stdin, stdout, stderr = ssh.exec_command('echo "skip - would take 4min"')
stdin, stdout, stderr = ssh.exec_command('tail -5 /var/log/hr-pipeline.log 2>&1')
print('\n=== LAST LOG LINES ===')
print(stdout.read().decode('utf-8', errors='replace'))

# Check if there's a mail.log for cron
stdin, stdout, stderr = ssh.exec_command('grep -i "cron\|Cron" /var/log/mail.log 2>/dev/null | tail -5; echo "---"; grep -i "cron\|Cron" /var/log/debug 2>/dev/null | tail -5; echo "---"; ls /var/log/ 2>/dev/null')
print('\n=== LOG FILES ===')
out = stdout.read().decode('utf-8', errors='replace')
print(out)

ssh.close()
