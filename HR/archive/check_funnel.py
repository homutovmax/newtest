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

out, err, code = run('tailscale funnel --bg 8000 2>&1', 15)
print('Funnel:', out[:500])
if err: print('ERR:', err[:300])

time.sleep(3)

# Check serve/funnel status
out, _, _ = run('tailscale serve status 2>&1', 5)
print('Serve status:', out[:500])

out, _, _ = run('tailscale status 2>&1', 5)
print('\nStatus:', out)

# Get the funnel URL
out, _, _ = run("tailscale status --json 2>/dev/null | grep -oP '\"FQDN\":\"[^\"]+' | cut -d'\"' -f3 || echo no_fqdn", 5)
print('\nFQDN:', out[:200])

ssh.close()
