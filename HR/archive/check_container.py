import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

def run(cmd, timeout=10):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    return out

# Check container has needed files and deps
print('Container Python:', run('docker exec hr-web-1 python --version 2>&1', 5))
print('Container files:', run('docker exec hr-web-1 ls /app/update_vacancies.py 2>&1', 5))
print('Container requests:', run('docker exec hr-web-1 python -c "import requests; print(requests.__version__)" 2>&1', 5))
print('Container bs4:', run('docker exec hr-web-1 python -c "import bs4; print(bs4.__version__)" 2>&1', 5))

# Try running update_vacancies inside container (test mode)
# print('Test run:', run('docker exec hr-web-1 python update_vacancies.py 2>&1 | tail -5', 30))

# Check if alembic and migration run after pipeline
# Pipeline merges into JSON, then migration pushes to PG
# So the cron job should: update_vacancies.py -> migration -> done

ssh.close()
