import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

sftp = ssh.open_sftp()
sftp.put(r'C:\NEWTEST\HR\web\app.py', '/opt/hr/web/app.py', confirm=False)
sftp.put(r'C:\NEWTEST\HR\web\templates\analytics.html', '/opt/hr/web/templates/analytics.html', confirm=False)
sftp.close()
print('Uploaded')

ssh.exec_command('docker restart hr-web-1')
time.sleep(5)

import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(10)
s.connect(('100.112.4.123', 8000))
s.send(b'GET /analytics HTTP/1.0\r\nHost: test\r\n\r\n')
resp = b''
while True:
    c = s.recv(4096)
    if not c: break
    resp += c
s.close()
html = resp.decode('utf-8', errors='replace')
body = html.split('\r\n\r\n', 1)[1]
print('Length:', len(body))
print('Status:', html.split('\r\n')[0])

# Check key sections
for term in ['Проверки качества', 'Проблемные записи', 'без зарплаты', 'Без категории', 'длинным company']:
    if term in body:
        print(f'  [OK] содержит: {term}')
    else:
        print(f'  [--] НЕТ: {term}')

ssh.close()
