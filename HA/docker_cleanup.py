import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=15)

def run(cmd, timeout=15):
    try:
        stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
        return stdout.read().decode('utf-8', errors='replace').strip()
    except Exception as e:
        return f'ERR: {e}'

print('=== Docker images ===')
print(run('docker images 2>&1', 10))

print('\n=== Docker system df ===')
print(run('docker system df 2>&1', 10))

print('\n=== Container sizes ===')
print(run('docker ps -s --format "table {{.Names}}\t{{.Size}}" 2>&1', 10))

print('\n=== Prune unused ===')
print(run('docker builder prune -a -f 2>&1', 30))
print(run('docker image prune -a -f 2>&1', 30))

print('\n=== Docker volumes ===')
print(run('docker volume ls 2>&1', 10))

print('\n=== Final disk ===')
print(run('df -h / 2>&1', 5))

ssh.close()
