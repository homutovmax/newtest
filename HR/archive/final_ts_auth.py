import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

def run(cmd, timeout=10):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    return out

# Clean state
run('systemctl stop tailscaled')
run('rm -rf /var/lib/tailscale')
time.sleep(1)

# Restart fresh
run('systemctl start tailscaled')
time.sleep(3)

# Run tailscale up with nohup so it survives
run('nohup tailscale up > /tmp/ts_url_final.txt 2>&1 &')
time.sleep(5)

# Read URL
out = run('cat /tmp/ts_url_final.txt')
print(out[:500])

import re
urls = re.findall(r'https://[^\s]+', out)
for u in urls:
    print(f'\n=== ССЫЛКА ЖИВЁТ 5 МИНУТ ===')
    print(u)
    print('После Connect напишите "ок"')

# Keep SSH alive to prevent process from being killed
time.sleep(300)

ssh.close()
