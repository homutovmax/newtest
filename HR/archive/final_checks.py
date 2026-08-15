import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

def run(cmd, timeout=10):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    return out

print('=== Tailscale ===')
out = run('tailscale status 2>&1')
print(out)

out = run('tailscale ip -4 2>/dev/null || echo NO_IP')
print('IP:', out)

print('\n=== Postfix cleanup ===')
out = run('systemctl stop postfix; systemctl disable postfix 2>&1')
print('Postfix disabled:', out[:200])

print('\n=== Cron ===')
out = run('crontab -l')
print(out)

ssh.close()
