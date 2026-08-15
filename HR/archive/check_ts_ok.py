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
    run('kill %1 2>/dev/null')  # kill background tailscale up
    
    # Setup funnel
    print('\n=== Enable Funnel ===')
    out = run('tailscale funnel --bg 8000 2>&1')
    print('Funnel:', out[:500])
    
    time.sleep(2)
    
    # Get DNS name
    out = run("tailscale status --json 2>/dev/null | grep -oP 'https://[^\"]+' || echo no")
    print('Public URL:', out[:300])
    
    # Get the FQDN
    out = run("tailscale status --json 2>/dev/null | grep -oP 'Domain\":\"[^\"]+' | cut -d'\"' -f3 || echo no")
    print('Domain:', out[:200])
    
    # Direct URL
    print(f'\nДоступ через Tailscale IP: http://{ip}:8000')
    print(f'Доступ через Funnel: будет https://...')
else:
    print('Не подключился.')
    print('Проверьте https://login.tailscale.com/admin/machines — есть ли новое устройство?')
    # Kill background process
    run('kill %1 2>/dev/null')

ssh.close()
