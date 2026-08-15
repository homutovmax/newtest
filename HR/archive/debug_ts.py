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

out, err, _ = run('systemctl status tailscaled --no-pager 2>&1 | head -15')
print('tailscaled:', out)
if err: print('ERR:', err)

out, _, _ = run('journalctl -u tailscaled --no-pager -n 20 2>&1')
print('\nJournal:', out[:1000])

# Check if port 8000 is accessible from other tailnet members
out, _, _ = run('curl -s http://localhost:8000/health')
print('\nLocal health:', out[:100])

# Check listening ports
out, _, _ = run('ss -tlnp | grep -E "8000|:25"')
print('\nListening:', out[:300])

ssh.close()
