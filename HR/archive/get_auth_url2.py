import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

def run(cmd, timeout=10):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    return out

# Run tailscale up in background, capture output to file
run('tailscale up > /tmp/ts_out.txt 2>&1 & sleep 3; kill %1 2>/dev/null', timeout=10)

out = run('cat /tmp/ts_out.txt', 5)
print(out[:1000])

import re
urls = re.findall(r'https://[^\s]+', out)
for u in urls:
    print('\n=== OPEN IN BROWSER TO AUTHENTICATE ===')
    print(u)

ssh.close()
