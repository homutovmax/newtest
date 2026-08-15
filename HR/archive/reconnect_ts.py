import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

def run(cmd, timeout=15):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()[:300]
    return out, err, code

# Full reset
run('systemctl stop tailscaled')
run('rm -rf /var/lib/tailscale')
run('systemctl start tailscaled')
time.sleep(3)

# Get fresh URL silently
run('tailscale up > /tmp/ts_url2.txt 2>&1 & sleep 5; kill %1 2>/dev/null')
out, _, _ = run('cat /tmp/ts_url2.txt')
print('URL line:', out[:200])

import re
urls = re.findall(r'https://[^\s]+', out)
for u in urls:
    print(f'\nОТКРОЙТЕ В БРАУЗЕРЕ: {u}')
    print('Войдите через ТОТ ЖЕ аккаунт homutov.m@gmail.com')

ssh.close()
