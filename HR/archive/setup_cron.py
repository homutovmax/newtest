import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

def run(cmd, timeout=30):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()[:500]
    return out, err, code

# 1. Create cron script
script = '''#!/bin/bash
# HR Pipeline cron job — runs inside Docker
LOG=/var/log/hr-pipeline.log
echo "=== $(date) ===" >> $LOG
cd /opt/hr

# Run scraper + cover generator (takes ~3-4 min)
docker exec hr-web-1 python update_vacancies.py >> $LOG 2>&1
STATUS=$?
echo "update_vacancies: exit $STATUS" >> $LOG

# Sync to PostgreSQL
docker exec hr-web-1 python -m src.migration >> $LOG 2>&1
MSTATUS=$?
echo "migration: exit $MSTATUS" >> $LOG

echo "=== done ($STATUS/$MSTATUS) ===" >> $LOG
'''

out, err, code = run('cat > /opt/hr/run_pipeline.sh << '\''SCRIPT'\''\n' + script.replace('\n', '\\n') + '\nSCRIPT', 10)
# Actually let me use a different approach - write with python
print('Using heredoc approach...')

# Write script file line by line via Python
transport = ssh.get_transport()
channel = transport.open_session()
channel.exec_command('cat > /opt/hr/run_pipeline.sh')
channel.send(script.encode())
channel.shutdown_write()
code = channel.recv_exit_status()
print('Write:', code)

# Make executable
out, _, _ = run('chmod +x /opt/hr/run_pipeline.sh', 5)
print('Chmod:', out)

# 2. Add to crontab (daily at 8:00 AM)
out, _, _ = run('crontab -l 2>/dev/null', 5)
existing = out
print('Existing cron:', existing[:200])

new_cron = existing + '\n0 8 * * * /opt/hr/run_pipeline.sh\n' if existing else '0 8 * * * /opt/hr/run_pipeline.sh\n'

# Write new crontab
channel = transport.open_session()
channel.exec_command('crontab -')
channel.send(new_cron.encode())
channel.shutdown_write()
code = channel.recv_exit_status()
print('Crontab update:', code)

# Verify
out, _, _ = run('crontab -l', 5)
print('Final crontab:', out)

ssh.close()
