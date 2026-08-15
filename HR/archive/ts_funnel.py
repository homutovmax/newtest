import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

def run(cmd, timeout=15):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    return out, code

print('=== Setup Tailscale Funnel ===')
out, _ = run('tailscale funnel --bg 8000 2>&1', 10)
print('Funnel:', out[:500])

time.sleep(3)

# Get public URL
out, _ = run("tailscale status --json 2>/dev/null | grep -oP 'https://[^\"]+' || echo no_funnel_url", 5)
print('\nFunnel URL:', out[:300])

# Get the device's FQDN
out, _ = run('tailscale status 2>&1', 5)
print('\nUpdated status:')
print(out)

# Show the web app accessible
ip = '100.112.4.123'
print(f'\n=== ДОСТУПНО ===')
print(f'По Tailscale IP: http://{ip}:8000')
print(f'По Funnel URL:  {out[:200]}')

ssh.close()
