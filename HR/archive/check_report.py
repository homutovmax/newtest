import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=15)

stdin, stdout, stderr = ssh.exec_command('curl -s http://localhost:8000/report 2>&1 | head -20')
print(stdout.read().decode()[:1500])

print('---')
stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/report')
print('Status code:', stdout.read().decode())

ssh.close()
