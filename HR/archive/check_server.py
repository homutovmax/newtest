import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=15)

def run(cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()[:300]
    return out, err, code

print('=== SERVER INFO ===')
out, _, _ = run('cat /etc/os-release | head -3')
print(out)

out, _, _ = run('uname -m')
print('Arch:', out)

out, _, _ = run('which tailscale 2>/dev/null || echo "NOT INSTALLED"')
print('Tailscale:', out)

out, _, _ = run('which sendmail 2>/dev/null || echo "NOT INSTALLED"')
print('Sendmail:', out)

out, _, _ = run('which postfix 2>/dev/null || echo "NOT INSTALLED"')
print('Postfix:', out)

out, _, _ = run('curl -s -o /dev/null -w "%{http_code}" https://api.telegram.org 2>&1 || echo "FAIL"')
print('Telegram API:', out)

out, _, _ = run('ip addr show tailscale0 2>/dev/null | grep inet || echo "NO TAILSCALE IF"')
print('Tailscale IP:', out)

# Check existing cron
out, _, _ = run('crontab -l 2>/dev/null || echo "NO CRON"')
print('Crontab:', out[:500])

ssh.close()
