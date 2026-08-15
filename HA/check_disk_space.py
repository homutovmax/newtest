import paramiko, json

HOST = '192.168.1.92'
USER = 'root'
PASS = 'CHANGE_ME'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=10)

def exec(cmd, timeout=15):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    return stdout.read().decode('utf-8', errors='replace').strip()

# 1. Disk usage overview
print("=" * 60)
print("1. ОБЩИЙ РАЗМЕР ДИСКОВ")
print("=" * 60)
print(exec("df -h 2>&1"))

# 2. Top-level directory sizes
print("\n" + "=" * 60)
print("2. РАЗМЕРЫ КАТАЛОГОВ В / (top 20)")
print("=" * 60)
print(exec("du -sh /* 2>/dev/null | sort -rh | head -20"))

# 3. Docker disk usage
print("\n" + "=" * 60)
print("3. DOCKER ДИСК")
print("=" * 60)
print(exec("docker system df 2>&1"))

# 4. Docker container sizes
print("\n" + "=" * 60)
print("4. РАЗМЕРЫ DOCKER КОНТЕЙНЕРОВ")
print("=" * 60)
print(exec("docker ps --size --format 'table {{.Names}}\t{{.Size}}' 2>&1"))

# 5. Docker volumes
print("\n" + "=" * 60)
print("5. DOCKER VOLUMES")
print("=" * 60)
print(exec("docker volume ls 2>&1"))
print(exec("docker system df -v 2>&1 | head -40"))

# 6. Log files
print("\n" + "=" * 60)
print("6. БОЛЬШИЕ LOG-ФАЙЛЫ (>50MB)")
print("=" * 60)
print(exec("find /var/log -type f -size +50M -exec ls -lh {} \\; 2>/dev/null | sort -k5 -rh | head -20"))

# 7. All large files (>500MB)
print("\n" + "=" * 60)
print("7. ВСЕ ФАЙЛЫ >500MB")
print("=" * 60)
print(exec("find /DATA -type f -size +500M -exec ls -lh {} \\; 2>/dev/null | sort -k5 -rh | head -20"))

# 8. Docker container logs
print("\n" + "=" * 60)
print("8. РАЗМЕРЫ ЛОГОВ DOCKER КОНТЕЙНЕРОВ")
print("=" * 60)
for container in exec("docker ps --format '{{.Names}}' 2>&1").split('\n'):
    if container:
        log_size = exec(f"docker logs {container} 2>&1 | wc -c", timeout=5)
        print(f"  {container}: {int(log_size or 0):,} bytes")

# 9. Z2M logs specifically
print("\n" + "=" * 60)
print("9. Z2M ЛОГИ (размер + кол-во)")
print("=" * 60)
print(exec("ls -lh /DATA/AppData/big-bear-zigbee2mqtt/data/log/ 2>/dev/null | tail -20"))
print(exec("du -sh /DATA/AppData/big-bear-zigbee2mqtt/data/log/ 2>/dev/null"))

# 10. HA backup files
print("\n" + "=" * 60)
print("10. HA БЕКАПЫ")
print("=" * 60)
backup_paths = exec("find /DATA -path '*backup*' -o -path '*Backup*' 2>/dev/null | head -20")
if backup_paths:
    print(backup_paths)
print(exec("du -sh /DATA/AppData/homeassistant/config/backups/ 2>/dev/null"))

# 11. Docker unused images
print("\n" + "=" * 60)
print("11. НЕИСПОЛЬЗУЕМЫЕ DOCKER ОБРАЗЫ")
print("=" * 60)
print(exec("docker images --filter dangling=true 2>&1"))

# 12. Apt cache
print("\n" + "=" * 60)
print("12. APT КЭШ")
print("=" * 60)
print(exec("du -sh /var/cache/apt 2>/dev/null"))

# 13. Temporary files
print("\n" + "=" * 60)
print("13. /tmp содержимое")
print("=" * 60)
print(exec("du -sh /tmp/* 2>/dev/null | sort -rh | head -10"))
print(f"Total /tmp: {exec('du -sh /tmp 2>/dev/null')}")

# 14. Journald
print("\n" + "=" * 60)
print("14. JOURNALD")
print("=" * 60)
print(exec("journalctl --disk-usage 2>/dev/null"))

ssh.close()
