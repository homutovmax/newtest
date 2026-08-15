import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

def run(cmd, timeout=15):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    return out, code

# First check existing state
out, code = run('systemctl is-active tailscaled')
print('tailscaled:', out)

# Run tailscale up with authkey (non-blocking, short timeout)
out, code = run('timeout 15 tailscale up --authkey tskey-auth-kyyz6YUKh421CNTRL-HJ9zXZTgWJFyTGREQJ1eJFtNx7MixJKh --accept-dns=false 2>&1', 20)
print('Auth result:', code, out[:500])

time.sleep(3)

out, code = run('tailscale status 2>&1')
print('Status:', out)

out, code = run('tailscale ip -4 2>&1')
print('IP:', out)

if '100.' in out:
    print('\n=== CONNECTED! ===')

ssh.close()
