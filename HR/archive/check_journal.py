import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

def run(cmd, timeout=10):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    return out

# Kill stuck tailscale up
run('pkill tailscale 2>/dev/null; pkill tailscale 2>/dev/null')

# Check journal
out = run('journalctl -u tailscaled --no-pager -n 30 2>&1')
print(out[:2000])

# Check Windows status from here
# Try direct curl to the Windows Tailscale IP
# out = run('curl -s http://100.93.40.27:8000 2>&1 | head -5')
# print('Curl to windows:', out[:200])

ssh.close()
