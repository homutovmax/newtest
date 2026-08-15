import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

def run(cmd, timeout=10):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    return out

time.sleep(5)
out = run('tailscale status 2>&1')
print('Status:', out)

ip = run('tailscale ip -4 2>&1')
print('IP:', ip)

if '100.' in ip:
    print('\n=== CONNECTED! ===')
else:
    print('NOT connected. Checking logs...')
    out = run('journalctl -u tailscaled --no-pager -n 20 2>&1')
    print(out)

ssh.close()
