import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

def run(cmd, timeout=10):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    return out

# Make sure clean
run('systemctl stop tailscaled 2>/dev/null; rm -rf /var/lib/tailscale')
run('systemctl start tailscaled')
time.sleep(4)

# Use /dev/tty-style approach - run with timeout to capture output
stdin, stdout, stderr = ssh.exec_command(
    'timeout 10 tailscale up --accept-dns=false 2>&1 || true',
    timeout=20
)
time.sleep(5)
out = stdout.read().decode().strip()
err = stderr.read().decode().strip()
print('OUT:', out[:500])
print('ERR:', err[:500])

# The URL should be in the output
import re
urls = re.findall(r'https://[^\s]+', out + err)
for u in urls:
    print(f'\n=== ОТКРОЙТЕ ===')
    print(u)

ssh.close()
