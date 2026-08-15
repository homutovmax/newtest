import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

def run(cmd, timeout=10):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    return out

# Recreate run_pipeline.sh that was accidentally deleted  
channel = ssh.get_transport().open_session()
channel.exec_command('cat > /opt/hr/run_pipeline.sh')
channel.send(b"""#!/bin/bash
# HR Pipeline cron job
LOG=/var/log/hr-pipeline.log
echo "=== $(date) ===" >> $LOG
cd /opt/hr

# Run scraper + cover generator
docker exec hr-web-1 python update_vacancies.py >> $LOG 2>&1
STATUS=$?
echo "update_vacancies: exit $STATUS" >> $LOG

# Sync to PostgreSQL
docker exec hr-web-1 python -m src.migration >> $LOG 2>&1
MSTATUS=$?
echo "migration: exit $MSTATUS" >> $LOG

echo "=== done ===" >> $LOG
""")
channel.shutdown_write()
code = channel.recv_exit_status()
print('Write script:', code)

run('chmod +x /opt/hr/run_pipeline.sh')

# Verify cron
out = run('crontab -l')
print('Cron:', out)

# Verify script
out = run('ls -la /opt/hr/run_pipeline.sh')
print('Script:', out)

ssh.close()
