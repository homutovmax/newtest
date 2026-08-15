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

out, _, _ = run('tailscale status 2>&1')
print('Status:', out)

out, _, _ = run('tailscale ip -4')
print('IP:', out)

# Enable funnel
print('\n=== Setting up Tailscale Funnel ===')
out, _, _ = run('tailscale funnel --bg 8000 2>&1', 10)
print('Funnel:', out[:500])

# Get public URL
out, _, _ = run('tailscale status --json 2>/dev/null | grep -o "https://[^\"]*" || tailscale status 2>&1', 10)
print('URL:', out[:200])

ssh.close()
