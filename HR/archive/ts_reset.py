import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

def run(cmd, timeout=10):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    return out

# Kill any stale tailscale up processes
run("pkill -f 'tailscale up' 2>/dev/null; sleep 1")

# Use --reset flag to force fresh auth
run("nohup tailscale up --reset --accept-dns=false > /tmp/ts_reset.txt 2>&1 &")
time.sleep(8)

out = run("cat /tmp/ts_reset.txt 2>/dev/null || echo EMPTY")
print(out[:500])

import re
urls = re.findall(r'https://[^\s]+', out)
for u in urls:
    print(f'\n=== ОТКРОЙТЕ ===')
    print(u)
    print('На странице может быть кнопка "Connect" или список устройств.')

ssh.close()
