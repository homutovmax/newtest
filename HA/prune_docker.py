import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=15)

def run(cmd, timeout=30):
    try:
        stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
        return stdout.read().decode('utf-8', errors='replace').strip()
    except Exception as e:
        return f'ERR: {e}'

print("=== Текущий диск ===")
print(run("df -h / 2>&1", 5))

print("\n=== Удаление неиспользуемых Docker образов ===")
# First try to remove dangling images
print(run("docker image prune -a -f 2>&1", 60))

# Also clean up unused containers and networks
print("\n=== Очистка остановленных контейнеров и сетей ===")
print(run("docker container prune -f 2>&1", 30))
print(run("docker network prune -f 2>&1", 30))

print("\n=== Итоговый диск ===")
print(run("df -h / 2>&1", 5))

ssh.close()
