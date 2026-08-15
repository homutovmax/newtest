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

# Rebuild (Dockerfile changed)
code = run('cd /opt/hr && docker compose up -d --build web 2>&1', 60)
print('Rebuild:', code[0] if isinstance(code, tuple) else code)

time.sleep(5)
out, _, _ = run('curl -s http://localhost:8000/health')
print('Health:', out)

# Send test email from inside container
out, _, _ = run('docker exec hr-web-1 python -c "
from src.notifications.email import send_digest
send_digest(\"HR SMTP Test\", \"<h2>Test from Container</h2><p>SMTP via smtplib works!</p>\")
" 2>&1')
print('Test:', out[:500])

time.sleep(5)
out, _, _ = run('tail -5 /var/log/mail.log 2>&1')
print('Mail log:', out)

ssh.close()
print('=== DONE ===')
