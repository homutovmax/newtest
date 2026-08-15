import paramiko

HOST = '192.168.1.92'
USER = 'root'
PASS = 'CHANGE_ME'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=10)

def exec(cmd, timeout=30):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    return stdout.read().decode('utf-8', errors='replace').strip()

print("=== ДИСК: 58G всего, 51G занято, 6.2G свободно (90%) ===")

# 1. Top directories by size
print("\n=== Самые большие каталоги ===")
print(exec("du -sh /DATA/* /var/lib/docker /var/log /home /root /tmp 2>/dev/null | sort -rh | head -15", timeout=10))

# 2. Docker disk usage
print("\n=== Docker disk usage ===")
print(exec("docker system df 2>&1", timeout=10))

# 3. Docker container log sizes
print("\n=== Docker container log sizes (top 10) ===")
print(exec("find /var/lib/docker/containers -name '*-json.log' -exec ls -lh {} \\; 2>/dev/null | awk '{print $5, $NF}' | sort -rh | head -10", timeout=10))

# 4. Total Docker logs size
print(exec("du -sh /var/lib/docker/containers/*/*-json.log 2>/dev/null | awk '{print $1}' | paste -sd+ | bc 2>/dev/null || echo 'checking...'", timeout=10))

# 5. Unused Docker images
print("\n=== Docker images ===")
print(exec("docker images 2>&1", timeout=10))

# 6. HA backup size
print("\n=== HA backups ===")
print(exec("du -sh /DATA/AppData/homeassistant/config/backups/ 2>/dev/null", timeout=5))
print(exec("ls -lh /DATA/AppData/homeassistant/config/backups/ 2>/dev/null | head -10", timeout=5))

# 7. Docker volumes size
print("\n=== Docker volumes ===")
print(exec("docker volume ls 2>&1", timeout=5))
print(exec("du -sh /var/lib/docker/volumes/* 2>/dev/null | sort -rh | head -10", timeout=10))

# 8. Z2M logs
z2m_log_size = exec("du -sh /DATA/AppData/big-bear-zigbee2mqtt/data/log/ 2>/dev/null", timeout=5)
print(f"\n=== Z2M logs: {z2m_log_size} ===")
print(exec("ls -lt /DATA/AppData/big-bear-zigbee2mqtt/data/log/ 2>/dev/null | head -5", timeout=5))

# 9. Old Docker build cache
print("\n=== Docker build cache ===")
print(exec("docker builder prune -a --force 2>&1 || echo 'prune not available'", timeout=10))

# 10. CasaOS / tmp
print("\n=== CasaOS files ===")
print(exec("du -sh /var/lib/casaos 2>/dev/null", timeout=5))
print(exec("du -sh /DATA/.temp /DATA/.cache 2>/dev/null", timeout=5))

# 11. Значимые AppData каталоги
print("\n=== AppData каталоги >100MB ===")
print(exec("du -sh /DATA/AppData/*/ 2>/dev/null | sort -rh | head -20", timeout=10))

# 12. Docker контейнеры с размерами
print("\n=== Docker контейнеры (размер) ===")
print(exec("docker ps -s --format 'table {{.Names}}\t{{.Size}}' 2>&1", timeout=10))

ssh.close()
