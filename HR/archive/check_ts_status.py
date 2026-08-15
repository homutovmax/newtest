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

# Check tailscale auth status
out, _, _ = run('tailscale status 2>&1', 5)
print('Tailscale status:')
print(out)

# Get IP if authenticated
out, _, _ = run('tailscale ip -4 2>/dev/null || echo NOT_AUTH', 5)
print('\nTailscale IP:', out)

# Check what services are running
out, _, _ = run('docker ps --format "{{.Names}} {{.Status}}"', 5)
print('\nDocker containers:')
print(out)

ssh.close()
