import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

def run(cmd, timeout=15):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()[:300]
    return out, err, code

# Kill stale processes
run("pkill -f 'tailscale up' 2>/dev/null; pkill -f screen 2>/dev/null")
run('systemctl stop tailscaled; rm -rf /var/lib/tailscale; systemctl start tailscaled')
time.sleep(5)

# Use auth key
authkey = "tskey-auth-kyyz6YUKh421CNTRL-HJ9zXZTgWJFyTGREQJ1eJFtNx7MixJKh"
out, err, code = run(f"tailscale up --authkey {authkey} --accept-dns=false 2>&1", 20)
print('Auth:', code, out[:500], err[:200])

time.sleep(3)

out, _, _ = run('tailscale status 2>&1')
print('Status:', out)

ip, _, _ = run('tailscale ip -4 2>&1')
print('IP:', ip)

if '100.' in ip:
    print('\n=== TAILSCALE CONNECTED! ===')
    
    # Setup funnel
    out, _, _ = run('tailscale funnel --bg 8000 2>&1')
    print('Funnel:', out[:500])
    
    time.sleep(2)
    
    # Get Funnel URL
    out, _, _ = run("tailscale status --json 2>/dev/null | grep -oP 'https://[^\"]+' || echo nope")
    print('Public URL:', out[:300])
    
    # Get device name for URL
    out, _, _ = run("tailscale status --json 2>/dev/null | grep -oP 'Domain\":\"[^\"]+' | cut -d'\"' -f3 || tailscale status")
    print('Domain:', out[:200])
    
    print(f'\n=== АДРЕСА ===')
    print(f'Внутри Tailscale: http://{ip}:8000')
    print(f'В браузере Windows: http://{ip}:8000')

ssh.close()
