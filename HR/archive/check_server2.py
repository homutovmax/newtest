import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

def run(cmd, timeout=10):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()[:300]
    return out, err, code

print('OS:', run('cat /etc/os-release | head -1', 5)[0])
print('Arch:', run('uname -m', 5)[0])

# Check installed tools
for tool in ['tailscale', 'sendmail', 'postfix']:
    out, _, _ = run(f'which {tool} 2>/dev/null || echo MISSING', 5)
    print(f'{tool}:', out)

# Check if telegram is accessible (quick check - just connect to port 443)
out, _, _ = run('timeout 3 bash -c "echo > /dev/tcp/api.telegram.org/443" 2>/dev/null && echo OK || echo BLOCKED', 8)
print('Telegram API:', out)

# Check tailscale interface
out, _, _ = run('ip addr show tailscale0 2>/dev/null | grep inet || echo NO_TAILSCALE', 5)
print('Tailscale IP:', out)

# Check existing cron
out, _, _ = run('crontab -l 2>/dev/null || echo NO_CRON', 5)
print('Crontab:', out[:500])

ssh.close()
