import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

def run(cmd, timeout=10):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()[:300]
    return out, err, code

# Check what files are in /opt/hr
out, _, _ = run('ls -la /opt/hr/')
print('Files:', out)

# Check if update_vacancies.py exists
out, _, _ = run('ls /opt/hr/update_vacancies.py 2>/dev/null && echo EXISTS || echo NOT_FOUND')
print('update_vacancies.py:', out)

# Check what Python packages are available on server
out, _, _ = run('python3 -c "import requests; print(requests.__version__)" 2>&1 || echo NO_REQUESTS')
print('requests:', out)

# Check if we can just reuse the docker container
out, _, _ = run('docker exec hr-web-1 python -c "import os; print(os.listdir(\".\"))" 2>&1')
print('Container files:', out[:300])

ssh.close()
