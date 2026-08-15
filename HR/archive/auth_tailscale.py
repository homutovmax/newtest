import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

def run(cmd, timeout=15):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()[:500]
    return out, err, code

# Check service
out, _, _ = run('systemctl status tailscaled 2>&1 | head -10')
print('Service:', out[:500])

# Run tailscale up and get auth URL
print()
print('=== Running tailscale up ===')
# Use timeout to kill after 10s (it will hang waiting for auth)
stdin, stdout, stderr = ssh.exec_command('tailscale up 2>&1', timeout=10)
out = stdout.read().decode().strip()
err = stderr.read().decode().strip()
print('Output:', out[:500])
print('Stderr:', err[:300])

ssh.close()
