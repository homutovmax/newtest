import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

def run(cmd, timeout=15):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()[:300]
    return out, err, code

# Upload script
sftp = ssh.open_sftp()
sftp.put(r'C:\NEWTEST\HR\run_pipeline.sh', '/opt/hr/run_pipeline.sh', confirm=False)
sftp.close()
print('Uploaded run_pipeline.sh')

# Make executable
out, _, _ = run('chmod +x /opt/hr/run_pipeline.sh')
print('Chmod:', out)

# Get existing crontab
out, _, _ = run('crontab -l 2>/dev/null || echo ""')
existing = out

# Add pipeline cron (daily at 8:00 AM)
cron_line = '0 8 * * * /opt/hr/run_pipeline.sh'
if cron_line not in existing:
    new_cron = existing.strip() + '\n' + cron_line + '\n' if existing.strip() else cron_line + '\n'
    
    transport = ssh.get_transport()
    channel = transport.open_session()
    channel.exec_command('crontab -')
    channel.send(new_cron.encode())
    channel.shutdown_write()
    code = channel.recv_exit_status()
    print('Crontab update:', code)
else:
    print('Cron already exists')

# Verify
out, _, _ = run('crontab -l')
print('Final crontab:')
print(out)

ssh.close()
