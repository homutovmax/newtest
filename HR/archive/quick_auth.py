import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

def run(cmd, timeout=15):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    return out

# Restart daemon
run('systemctl restart tailscaled')
time.sleep(3)

# Run tailscale up with timeout of 60s to keep URL alive longer
stdin, stdout, stderr = ssh.exec_command('tailscale up 2>&1', timeout=60)

# Give it a moment to print the URL
import select
time.sleep(3)

# Read available data
out = ''
while True:
    try:
        chunk = stdout.read(4096)
        if not chunk:
            break
        out += chunk.decode()
    except:
        break

print(out)

import re
urls = re.findall(r'https://[^\s]+', out)
for u in urls:
    print(f'\n=== БЫСТРО ОТКРОЙТЕ: {u} ===')

ssh.close()
