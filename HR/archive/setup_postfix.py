import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

def run(cmd, timeout=30):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()[:500]
    return out, err, code

# Upload updated docker-compose.yml
sftp = ssh.open_sftp()
sftp.put(r'C:\NEWTEST\HR\docker-compose.yml', '/opt/hr/docker-compose.yml', confirm=False)
sftp.close()
print('Uploaded docker-compose.yml')

# Rebuild with new volume config
out, err, code = run('cd /opt/hr && docker compose up -d --build web 2>&1', 60)
print('Rebuild:', code)
time.sleep(5)

# Check status
out, _, _ = run('docker inspect -f {{.State.Status}} hr-web-1')
print('Status:', out)

# Health
out, _, _ = run('curl -s http://localhost:8000/health')
print('Health:', out[:100])

# Now install postfix
print('\n=== Installing postfix ===')
out, err, code = run('apt-get update -qq 2>&1 | tail -1', 30)
print('Apt update:', code)

# Install postfix non-interactively
out, err, code = run('DEBIAN_FRONTEND=noninteractive apt-get install -y postfix mailutils 2>&1 | tail -5', 60)
print('Postfix install:', code, out[-200:] if out else '')

# Configure postfix for local-only + relay
out, _, _ = run('postconf -e "myhostname=hr-server.tailnet.local" 2>&1', 5)
out, _, _ = run('postconf -e "inet_interfaces=loopback-only" 2>&1', 5)
out, _, _ = run('postconf -e "mydestination=localhost.localdomain, localhost" 2>&1', 5)

# Restart postfix
out, _, _ = run('systemctl restart postfix', 10)
print('Postfix restarted')

# Test sendmail
out, _, _ = run('echo "Test from HR server" | sendmail -v homutov.m@gmail.com 2>&1 | head -10', 10)
print('Sendmail test:', out[:300])

ssh.close()
