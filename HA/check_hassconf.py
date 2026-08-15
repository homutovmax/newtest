import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=15)

def run(cmd, timeout=10):
    try:
        stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
        return stdout.read().decode('utf-8', errors='replace').strip()
    except Exception as e:
        return f'ERR: {e}'

print("=== Image ===")
print(run('docker inspect hassconf --format "Image: {{.Config.Image}}" 2>&1', 10))

print("\n=== Cmd ===")
print(run('docker inspect hassconf --format "Cmd: {{.Config.Cmd}}" 2>&1', 10))

print("\n=== Created ===")
print(run('docker inspect hassconf --format "Created: {{.Created}}" 2>&1', 10))

print("\n=== Mounts ===")
print(run('docker inspect hassconf --format "{{range .Mounts}}{{.Source}} -> {{.Destination}}{{\"\\n\"}}{{end}}" 2>&1', 10))

print("\n=== Status ===")
print(run('docker inspect hassconf --format "Status: {{.State.Status}}, Started: {{.State.StartedAt}}" 2>&1', 10))

print("\n=== Image details ===")
print(run('docker images | grep hassconf', 10))

print("\n=== Logs ===")
print(run('docker logs hassconf --tail 20 2>&1', 10))

print("\n=== Restart count ===")
print(run('docker inspect hassconf --format "Restarts: {{.RestartCount}}" 2>&1', 10))

ssh.close()
