import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

# Read the local file and write to remote via SFTP
with open(r'C:\NEWTEST\HR\web\app.py', 'r', encoding='utf-8') as f:
    content = f.read()

sftp = ssh.open_sftp()
with sftp.open('/opt/hr/web/app.py', 'wb') as f:
    f.write(content.encode('utf-8'))
print('Uploaded app.py')

with open(r'C:\NEWTEST\HR\web\templates\analytics.html', 'r', encoding='utf-8') as f:
    content = f.read()

with sftp.open('/opt/hr/web/templates/analytics.html', 'wb') as f:
    f.write(content.encode('utf-8'))
print('Uploaded analytics.html')
sftp.close()

# Restart
ssh.exec_command('docker restart hr-web-1')
time.sleep(5)

# Verify
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(10)
s.connect(('100.112.4.123', 8000))
s.send(b'GET /analytics HTTP/1.0\r\nHost: test\r\n\r\n')
resp = b''
while True:
    c = s.recv(16384)
    if not c: break
    resp += c
s.close()
parts = resp.decode('utf-8', errors='replace').split('\r\n\r\n', 1)
body = parts[1] if len(parts) > 1 else ''
print('Status:', resp.decode()[:30])
print('Length:', len(body))

for term in ['Проверки качества', 'Проблемные записи', 'без зарплаты']:
    print(f'  {"[OK]" if term in body else "[--]"} {term}')

ssh.close()
