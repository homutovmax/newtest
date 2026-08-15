import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

def run(cmd, timeout=10):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    return out

# Check if tailscale up is still running
out = run('ps aux | grep "tailscale up" | grep -v grep')
print('Running processes:', out[:300])

# Check tailscaled status
out = run('journalctl -u tailscaled --no-pager -n 15 2>&1')
print('\nJournal:')
print(out)

# Take a different approach: check if both Windows and server can see each other
# from Windows side, check the PowerShell output we saw earlier
print('\n=== From the earlier Windows check: ===')
print('Windows has: 100.93.40.27 (laptop-tjiblagu)')
print('Server was seen as: ibox-z3-1 (offline), ibox-z3 (offline)')

# Try running tailscale up interactively with a longer SSH session
print('\nOld devices may be blocking. Let me try to fix this...')

ssh.close()
