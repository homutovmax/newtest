import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

def run(cmd, timeout=10):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()[:500]
    return out, err, code

# Check mail queue
print('=== Mail queue ===')
out, _, _ = run('mailq 2>&1')
print(out[:500])

print('\n=== Mail logs ===')
out, _, _ = run('tail -30 /var/log/mail.log 2>&1')
print(out[:1000])

# Check if postfix is running
print('\n=== Postfix status ===')
out, _, _ = run('systemctl status postfix --no-pager 2>&1 | head -10')
print(out)

# Check web health
print('\n=== Web health ===')
out, _, _ = run('curl -s http://localhost:8000/health')
print(out[:100])

print('\n=== Report page ===')
out, _, _ = run('curl -s http://localhost:8000/report 2>&1 | head -5')
print(out[:300])

ssh.close()
