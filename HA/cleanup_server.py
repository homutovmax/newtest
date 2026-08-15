import paramiko, time

HOST = '192.168.1.92'
USER = 'root'
PASS = 'CHANGE_ME'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=15)

def run(cmd, timeout=30):
    try:
        stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
        return stdout.read().decode('utf-8', errors='replace').strip()
    except Exception as e:
        return f"ERR: {e}"

# 1. Docker system space
print("=== Docker disk usage ===")
print(run("docker system df 2>&1", 10))

# 2. Docker images
print("\n=== Docker images ===")
print(run("docker images 2>&1", 10))

# 3. Docker volumes
print("\n=== Docker volumes ===")
print(run("docker volume ls 2>&1", 5))

# 4. AppData directory sizes
print("\n=== AppData sizes (MB, sorted) ===")
print(run("du -sm /DATA/AppData/*/ 2>/dev/null | sort -rn | head -15", 20))

# 5. Docker logs size
print("\n=== Docker log sizes ===")
print(run("ls -lh /var/lib/docker/containers/*/*-json.log 2>/dev/null | awk '{print $5, $NF}' | sed 's|.*/containers/||;s|/.*||' | sort -rn | head -15", 10))

# 6. Total Docker log size sum
print(run("find /var/lib/docker/containers -name '*-json.log' -exec du -ch {} + 2>/dev/null | grep total$", 10))

# 7. Container sizes
print("\n=== Container sizes ===")
print(run("docker ps -s --format 'table {{.Names}}\t{{.Size}}' 2>&1", 10))

# 8. HA backups
print("\n=== HA backups ===")
print(run("du -sh /DATA/AppData/homeassistant/config/backups/ 2>/dev/null; ls -lh /DATA/AppData/homeassistant/config/backups/ 2>/dev/null", 10))

# 9. Z2M logs
print("\n=== Z2M logs ===")
print(run("du -sh /DATA/AppData/big-bear-zigbee2mqtt/data/log/ 2>/dev/null; ls -la /DATA/AppData/big-bear-zigbee2mqtt/data/log/*/ 2>/dev/null | head -20", 10))

# 10. Old Docker build cache
print("\n=== Docker build cache prune ===")
print(run("docker builder prune -a -f 2>&1", 20))

# 11. Unused docker resources
print("\n=== Docker system prune (dry-run) ===")
print(run("docker system prune -a -f 2>&1", 30))

# 12. Journald logs
print("\n=== Journald ===")
print(run("journalctl --disk-usage 2>/dev/null; journalctl --vacuum-size=200M 2>/dev/null; journalctl --disk-usage 2>/dev/null", 20))

# 13. Apt cache
print("\n=== APT cache cleanup ===")
print(run("du -sh /var/cache/apt; apt clean 2>&1; du -sh /var/cache/apt", 15))

# 14. /tmp large files
print("\n=== /tmp cleanup ===")
print(run("du -sh /tmp/* 2>/dev/null | sort -rh | head -5", 5))
print(run("rm -rf /tmp/*.py /tmp/*.log /tmp/ha_* 2>/dev/null; echo '/tmp cleaned'", 5))

# 15. Old Z2M logs (keep last 3)
print("\n=== Z2M log dirs cleanup ===")
print(run("ls -d /DATA/AppData/big-bear-zigbee2mqtt/data/log/*/ 2>/dev/null | head -5", 5))
dirs = run("ls -d /DATA/AppData/big-bear-zigbee2mqtt/data/log/*/ 2>/dev/null", 5)
if dirs and 'ERR' not in dirs:
    log_dirs = [d for d in dirs.split('\n') if d.strip()]
    if len(log_dirs) > 3:
        print(f"Removing {len(log_dirs)-3} old log dirs...")
        for d in log_dirs[:-3]:
            r = run(f"rm -rf '{d}'", 10)
            if r:
                print(f"  Removed: {d}")
        print(run("du -sh /DATA/AppData/big-bear-zigbee2mqtt/data/log/ 2>/dev/null"))

# Final summary
print("\n" + "=" * 60)
print("FINAL DISK USAGE")
print("=" * 60)
print(run("df -h / 2>&1", 5))

ssh.close()
