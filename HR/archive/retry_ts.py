import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

def run(cmd, timeout=10):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    return out

# Restart and wait
run('systemctl restart tailscaled')
time.sleep(5)

# Check
out = run('tailscale status 2>&1')
print('Status:', out)

out = run('tailscale ip -4 2>&1')
print('IP:', out)

if '100.' in out:
    print('\n=== TAILSCALE WORKS ===')
    # Get DNS name
    out = run('tailscale status --json 2>/dev/null || tailscale status')
    print('Full:', out[:500])
    
    # Setup funnel
    print('\nSetting up Tailscale Funnel...')
    out = run('tailscale funnel --bg 8000 2>&1')
    print('Funnel:', out[:500])
    
    # Get public URL
    time.sleep(2)
    out = run("tailscale status --json 2>/dev/null | grep -oP 'https://[^\"]+' || curl -s http://localhost:8000/health")
    print('Public URL check:', out[:200])
else:
    print('Not authenticated yet.')
    print('1. Open https://login.tailscale.com and check if device shows up')
    print('2. Or try: tailscale up --accept-risk --reset')

ssh.close()
