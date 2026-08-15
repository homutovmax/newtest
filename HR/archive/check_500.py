import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

stdin, stdout, stderr = ssh.exec_command('docker logs hr-web-1 --tail 30 2>&1')
print(stdout.read().decode()[:2000])
ssh.close()
