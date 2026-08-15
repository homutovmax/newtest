import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

def run(cmd, timeout=15):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()[:500]
    return out, err, code

sftp = ssh.open_sftp()
for f in ['Dockerfile', 'docker-compose.yml', 'src/config.py', 'src/notifications/email.py']:
    sftp.put(f'C:\\NEWTEST\\HR\\{f}', f'/opt/hr/{f.replace("/", "/")}', confirm=False)
    print(f'Uploaded {f}')
sftp.close()

# Add SMTP_PASSWORD to .env
run("""cat >> /opt/hr/.env << 'EOF'
SMTP_HOST=smtp.yandex.ru
SMTP_PORT=587
SMTP_USER=maximumkh@yandex.ru
SMTP_PASSWORD=CHANGE_ME
EMAIL_FROM=maximumkh@yandex.ru
EMAIL_TO=homutov.m@gmail.com
EOF""")
print('Updated .env')

# Rebuild
out, err, code = run('cd /opt/hr && docker compose up -d --build web 2>&1', 60)
print('Rebuild:', code)
time.sleep(5)

out, _, _ = run('curl -s http://localhost:8000/health')
print('Health:', out)

# Test smtplib
transport = ssh.get_transport()
channel = transport.open_session()
channel.exec_command('docker exec hr-web-1 python -c "' + '''
from src.notifications.email import send_digest
send_digest("HR SMTP Test", "<h2>Test from Container</h2><p>SMTP via smtplib works!</p>")
''' + '" 2>&1')
code = channel.recv_exit_status()
out = channel.recv(4096).decode('utf-8', errors='replace')
print('Test output:', out)

ssh.close()
print('=== DONE ===')
