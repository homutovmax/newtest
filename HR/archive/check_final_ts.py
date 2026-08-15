import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

def run(cmd, timeout=10):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    return out

time.sleep(5)

out = run('tailscale status 2>&1')
print('Status:', out)

ip = run('tailscale ip -4 2>&1')
print('IP:', ip)

if '100.' in ip:
    print('\n=== TAILSCALE CONNECTED ===')
    
    out = run('tailscale funnel --bg 8000 2>&1')
    print('Funnel:', out[:500])
    
    time.sleep(2)
    
    # Get Funnel URL
    out = run("tailscale status --json 2>/dev/null | grep -oP 'https://[^\"]+' || curl -s http://localhost:8000/health")
    print('Public URL:', out[:300])
    
    print(f'\n=== Доступно ===')
    print(f'Внутри Tailscale: http://{ip}:8000')
    print(f'В браузере Windows: http://{ip}:8000')
else:
    print('NOT connected yet')
    run('kill %1 2>/dev/null; pkill -f "tailscale up" 2>/dev/null')

ssh.close()
