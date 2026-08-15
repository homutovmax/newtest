import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

def run(cmd, timeout=10):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    return out

run('systemctl stop tailscaled 2>/dev/null; rm -rf /var/lib/tailscale; systemctl start tailscaled')
time.sleep(5)

# Run tailscale up in a way that keeps running
transport = ssh.get_transport()
channel = transport.open_session()
channel.setblocking(0)
channel.exec_command('tailscale up --accept-dns=false 2>&1')
time.sleep(8)

# Try to read what's available
out = b''
try:
    while True:
        chunk = channel.recv(4096)
        if not chunk:
            break
        out += chunk
except:
    pass

result = out.decode('utf-8', errors='replace')
print(result[:1000])

import re
urls = re.findall(r'https://[^\s]+', result)
for u in urls:
    print(f'\n=== ССЫЛКА АКТИВНА — ОТКРОЙТЕ ===')
    print(u)

ssh.close()
