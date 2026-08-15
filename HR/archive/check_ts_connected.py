import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

def run(cmd, timeout=10):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    return out

time.sleep(3)

out = run('tailscale status 2>&1')
print('Status:', out)

ip = run('tailscale ip -4 2>&1')
print('IP:', ip)

if '100.' in ip:
    print('\n=== TAILSCALE CONNECTED ===')
    
    # Enable funnel
    print('Setting up Funnel...')
    out = run('tailscale funnel --bg 8000 2>&1')
    print('Funnel:', out[:500])
    
    time.sleep(2)
    
    # Get public URL via DNS name
    out = run('tailscale status --json 2>/dev/null | grep -oP "https://[^\"]+" || echo "check tailscale status"')
    print('Public URL:', out[:300])
    
    # Show machine name
    out = run('tailscale status --json 2>/dev/null || tailscale status')
    # Try to extract name
    for line in out.split('\n'):
        if 'ibox' in line.lower() or 'server' in line.lower():
            print('Found:', line)
    
    # Or just use the IP directly
    print(f'\nДоступно по IP: http://{ip}:8000')
    print('В браузере Windows: http://100.x.x.x:8000')

ssh.close()
