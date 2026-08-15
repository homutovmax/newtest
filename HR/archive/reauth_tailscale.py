import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

def run(cmd, timeout=10):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    code = stdout.channel.recv_exit_status()
    return stdout.read().decode().strip()

# Stop old tailscaled, clear state, restart
run('systemctl stop tailscaled')
run('rm -rf /var/lib/tailscale')
run('systemctl start tailscaled')
time.sleep(2)

# Get fresh auth URL
run('tailscale up > /tmp/ts_url.txt 2>&1 & sleep 4; kill %1 2>/dev/null')
out = run('cat /tmp/ts_url.txt')
print(out)

import re
urls = re.findall(r'https://[^\s]+', out)
for u in urls:
    print('\n=== ОТКРОЙТЕ В БРАУЗЕРЕ ===')
    print(u)
    print('''   
1. Войдите через Google/Apple/Microsoft
2. Нажмите "Connect"
3. Напишите мне "готово"
''')

ssh.close()
