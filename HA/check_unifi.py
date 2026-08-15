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

print("=== Container info ===")
print(run('docker inspect unifi-controller --format "Image: {{.Config.Image}}" 2>&1', 10))
print(run('docker inspect unifi-controller --format "Created: {{.Created}}" 2>&1', 10))
print(run('docker inspect unifi-controller --format "Ports: {{json .NetworkSettings.Ports}}" 2>&1', 10))
print(run('docker inspect unifi-controller --format "Size: {{.SizeRootFs}}" 2>&1', 10))

print("\n=== Image ===")
print(run('docker images | grep unifi', 10))

print("\n=== Logs (last 20) ===")
print(run('docker logs unifi-controller --tail 20 2>&1', 10))

print("\n=== AppData size ===")
print(run('du -sh /DATA/AppData/unifi-controller/ 2>&1', 10))
print(run('du -sh /DATA/AppData/unifi-controller/*/ 2>&1 | sort -rh', 10))

ssh.close()
