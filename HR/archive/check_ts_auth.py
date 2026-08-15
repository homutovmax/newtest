import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

def run(cmd, timeout=10):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    code = stdout.channel.recv_exit_status()
    return stdout.read().decode().strip()

out = run('tailscale status 2>&1', 10)
print('Status:', out)

out = run('tailscale ip -4 2>/dev/null || echo "NOT AUTHENTICATED"', 5)
print('IP:', out)

ssh.close()
