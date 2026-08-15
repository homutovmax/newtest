import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=15)

def run(cmd, timeout=15):
    try:
        stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
        return stdout.read().decode('utf-8', errors='replace').strip()
    except Exception as e:
        return f'ERR: {e}'

time.sleep(10)

print("=== Docker status ===")
print(run("systemctl is-active docker", 10))

print("\n=== Running containers ===")
print(run("docker ps --format '{{.Names}} {{.Status}}' 2>&1", 10))

print("\n=== Test prune ===")
print(run("docker image prune -a -f --filter 'until=24h' 2>&1", 30))

print("\n=== Disk ===")
print(run("df -h / 2>&1", 5))

print("\n=== Log rotation applied ===")
print(run("docker inspect homeassistant | grep -A5 log-opts 2>/dev/null | head -10", 10))

ssh.close()
