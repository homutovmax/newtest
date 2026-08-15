import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=15)
stdin, stdout, stderr = ssh.exec_command('pip show starlette jinja2 fastapi 2>&1')
print(stdout.read().decode()[:500])
stderr = stderr.read().decode().strip()
if stderr: print('ERR:', stderr[:200])
ssh.close()
