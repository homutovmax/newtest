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

# Use separate commands instead of shell chain
run("nohup tailscale up --accept-dns=false > /tmp/ts_out.txt 2>&1 &", timeout=5)
time.sleep(8)

out = run("cat /tmp/ts_out.txt 2>/dev/null || echo EMPTY")
print('1:', out[:500])

if out == 'EMPTY' or not out.strip():
    time.sleep(8)
    out = run("cat /tmp/ts_out.txt 2>/dev/null || echo EMPTY2")
    print('2:', out[:500])

import re
urls = re.findall(r'https://[^\s]+', out)
for u in urls:
    print('\n=== SSYLKA AKTIVNA ===')
    print(u)

ssh.close()
