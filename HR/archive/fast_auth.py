import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

def run(cmd, timeout=10):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    return out

# Run in background, capture to file
run('systemctl restart tailscaled')
time.sleep(3)
run('tailscale up > /tmp/ts_auth.txt 2>&1 &')
time.sleep(4)

# Read the output
out = run('cat /tmp/ts_auth.txt 2>/dev/null')
print(out[:500])

import re
urls = re.findall(r'https://[^\s]+', out)
for u in urls:
    print(f'\n=== ОТКРОЙТЕ В БРАУЗЕРЕ ===')
    print(u)
    print('Если не сработает через 30 сек, напишите "не работает"')

ssh.close()
