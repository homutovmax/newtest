import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

def run(cmd, timeout=15):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    return out, err, code

out, err, code = run('timeout 10 tailscale funnel --bg 8000 2>&1', 15)
print('Funnel:', code, out[:500])
if err: print('ERR:', err[:300])

time.sleep(2)

out, _, _ = run('tailscale status 2>&1', 5)
print('\nStatus:')
print(out)

out, _, _ = run("tailscale status --json 2>/dev/null | grep -oP 'https://[^\"]+' || echo no_funnel", 5)
print('\nFunnel URL:', out[:300])

# Check if funnel is enabled
out, _, _ = run('tailscale funnel status 2>&1 || echo "no funnel status"', 5)
print('\nFunnel status:', out[:300])

ssh.close()
