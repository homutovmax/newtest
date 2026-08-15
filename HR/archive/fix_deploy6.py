import paramiko, time, os

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=15)

def run(cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()[:300] if stderr.readable() else ''
    if out: print(out)
    if err and code != 0: print('ERR:', err)
    return code

sftp = ssh.open_sftp()
sftp.put(r'C:\NEWTEST\HR\web\app.py', '/opt/hr/web/app.py', confirm=False)
print('Uploaded web/app.py')
sftp.close()

print('Rebuilding...')
run('cd /opt/hr && docker compose up -d --build web 2>&1')
time.sleep(5)

run('docker inspect -f {{.State.Status}} hr-web-1')

import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(10)
s.connect(('192.168.1.92', 8000))
s.send(b'GET /report HTTP/1.0\r\nHost: 192.168.1.92\r\n\r\n')
resp = s.recv(4096).decode('utf-8', errors='replace')
s.close()
print('First line:', resp.split('\r\n')[0])
if '200' in resp:
    print('SUCCESS - /report works')
else:
    print(resp[:500])

ssh.close()
print('=== DONE ===')
