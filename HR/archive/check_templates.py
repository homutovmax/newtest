import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=15)

stdin, stdout, stderr = ssh.exec_command('docker exec hr-web-1 python -c "import inspect; from starlette.templating import Jinja2Templates; print(inspect.getsource(Jinja2Templates.TemplateResponse))" 2>&1')
data = stdout.read().decode()[:3000]
print(data)
ssh.close()
