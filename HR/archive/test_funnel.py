import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

def run(cmd, timeout=10):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    return out

# Test funnel URL locally
out = run('curl -sk https://ibox-z3-2.taila7bc1e.ts.net/health 2>&1')
print('Funnel health:', out[:200])

out = run('curl -sk https://ibox-z3-2.taila7bc1e.ts.net/report 2>&1 | head -5')
print('Funnel report:', out[:200])

ssh.close()
