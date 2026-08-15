import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

sftp = ssh.open_sftp()

files = [
    (r'C:\NEWTEST\HR\generate_cover.py', '/opt/hr/generate_cover.py'),
    (r'C:\NEWTEST\HR\web\templates\report.html', '/opt/hr/web/templates/report.html'),
    (r'C:\NEWTEST\HR\web\static\style.css', '/opt/hr/web/static/style.css'),
]
for src, dst in files:
    with open(src, 'rb') as f:
        f_data = f.read()
    with sftp.open(dst, 'wb') as f:
        f.write(f_data)
    print(f'Uploaded {src.split(chr(92))[-1]} ({len(f_data)}b)')
sftp.close()

# Re-run migration to recategorize
print('\nClearing categories...')
stdin, stdout, stderr = ssh.exec_command(
    'docker exec hr-web-1 python -c "import psycopg2; conn = psycopg2.connect(\'postgresql://hr:hr@db/hr\'); cur = conn.cursor(); cur.execute(\'UPDATE vacancies SET category = NULL\'); conn.commit()"',
    timeout=10
)
print(stdout.read().decode()[:200])
stderr = stderr.read().decode().strip()
if stderr: print('ERR:', stderr[:200])

time.sleep(2)

print('Re-migrating...')
stdin, stdout, stderr = ssh.exec_command('docker exec hr-web-1 python -m src.migration 2>&1', timeout=30)
print(stdout.read().decode()[:500])

ssh.exec_command('docker restart hr-web-1')
time.sleep(5)

# Verify
import socket
for tab in ['telecom', 'ai', 'strategy', 'ba', 'other']:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(10)
    s.connect(('100.112.4.123', 8000))
    s.send(f'GET /report?tab={tab} HTTP/1.0\r\nHost: test\r\n\r\n'.encode())
    resp = b''
    while True:
        c = s.recv(16384)
        if not c: break
        resp += c
    s.close()
    body = resp.decode('utf-8', errors='replace').split('\r\n\r\n', 1)[1]
    vcount = body.count('<div class="vacancy">')
    print(f'  {tab:10s}: {vcount}')

# Check button
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(10)
s.connect(('100.112.4.123', 8000))
s.send(b'GET /report HTTP/1.0\r\nHost: test\r\n\r\n')
resp = b''
while True:
    c = s.recv(16384)
    if not c: break
    resp += c
s.close()
html = resp.decode('utf-8', errors='replace')
if 'analytics-btn' in html:
    print('\n[OK] Кнопка аналитики есть')

ssh.close()
print('\n=== DONE ===')
