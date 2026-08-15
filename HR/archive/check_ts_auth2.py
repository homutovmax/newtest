import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

def run(cmd, timeout=10):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    return out

out = run('tailscale status 2>&1')
print('Status:', out)

ip = run('tailscale ip -4 2>/dev/null || echo NO')
print('IP:', ip)

hostname = run('tailscale status --json 2>/dev/null | grep -o "\"DNSName\":\"[^\"]*\"" || echo no')
print('DNS:', hostname)

# Setup funnel
print('\nSetting up Funnel...')
out = run('tailscale funnel --bg 8000 2>&1')
print('Funnel:', out[:500])

# Get machine name
out = run('tailscale status --json 2>/dev/null | grep -oP \"DeviceName\":\"[^\"]+\" || tailscale status')
print('Name:', out[:200])

ssh.close()
