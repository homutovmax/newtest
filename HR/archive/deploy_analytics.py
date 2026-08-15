import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

sftp = ssh.open_sftp()
sftp.put(r'C:\NEWTEST\HR\web\templates\analytics.html', '/opt/hr/web/templates/analytics.html', confirm=False)
sftp.close()
print('Uploaded')

# Restart web
ssh.exec_command('docker restart hr-web-1')
time.sleep(5)

# Test
stdin, stdout, stderr = ssh.exec_command('curl -s http://localhost:8000/analytics 2>&1 | head -20')
print(stdout.read().decode()[:1000])

stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/analytics')
print('Status:', stdout.read().decode())

ssh.close()
