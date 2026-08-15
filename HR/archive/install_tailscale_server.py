import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

def run(cmd, timeout=30):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()[:500]
    return out, err, code

# Install Tailscale
print('=== Installing Tailscale ===')
out, err, code = run('curl -fsSL https://tailscale.com/install.sh 2>&1 | sh', timeout=60)
print('Install:', out[:500])
if err: print('ERR:', err[:300])

# Verify
out, _, _ = run('which tailscale && tailscale version', 5)
print('Version:', out[:200])

# Enable and start
out, _, _ = run('systemctl enable --now tailscaled', 10)
print('Service:', out[:200])

# Authenticate
print()
print('=== TO AUTHENTICATE, run on the server: ===')
print('tailscale up')

ssh.close()
