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

# Check if there are stopped containers
print("=== Stopped containers ===")
print(run("docker ps -a --format 'table {{.Names}}\t{{.Status}}\t{{.Size}}' 2>&1 | head -20", 10))

# Check dangling images specifically
print("\n=== Dangling images ===")
print(run("docker images -f dangling=true -q 2>&1 | wc -l", 10))

# Remove dangling
print("\n=== Removing dangling images ===")
print(run("docker image prune -f 2>&1", 20))

# Check all Docker images with sizes
print("\n=== All Docker images ===")
print(run("docker images --format 'table {{.Repository}}\t{{.Tag}}\t{{.Size}}' 2>&1 | sort -k3 -h -r | head -20", 10))

# Check for unused volumes
print("\n=== Docker volume prune (dry) ===")
print(run("docker volume ls -q 2>&1 | wc -l", 5))

# Suggest manual cleanup items
print("\n=== SUGGESTED MANUAL CLEANUP ===")
print("1. HA backups: 96M - можно удалить старые (оставить последний)")
print(run("ls -lh /DATA/AppData/homeassistant/config/backups/ 2>&1", 5))

# Check unifi logs
print("\n=== Unifi logs size ===")
print(run("du -sh /DATA/AppData/unifi-controller/logs/ 2>/dev/null", 10))
print(run("du -sh /DATA/AppData/unifi-controller/data/ 2>/dev/null", 10))

# Node-RED
print("\n=== Node-RED size breakdown ===")
print(run("du -sh /DATA/AppData/node-red/*/ 2>/dev/null | sort -rh", 10))

# Homebridge
print("\n=== Homebridge size ===")
print(run("du -sh /DATA/AppData/big-bear-homebridge/*/ 2>/dev/null | sort -rh", 10))

ssh.close()
