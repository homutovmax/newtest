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

# Check existing crontab
print("=== Текущий crontab ===")
print(run("crontab -l 2>&1", 5))

# Create a cleanup script
cleanup_script = """#!/bin/bash
# Docker cleanup - runs weekly
echo "[$(date)] Starting Docker cleanup..."

# Remove unused images (keep last 2 tagged)
docker image prune -a -f --filter "until=24h" 2>&1 | tail -1

# Remove stopped containers older than 24h
docker container prune -f --filter "until=24h" 2>&1 | tail -1

# Remove unused networks
docker network prune -f --filter "until=24h" 2>&1 | tail -1

# Remove build cache
docker builder prune -f --filter "until=24h" 2>&1 | tail -1

# Check HA backups - keep only last 3
BACKUP_DIR="/DATA/AppData/homeassistant/config/backups"
if [ -d "$BACKUP_DIR" ]; then
    COUNT=$(ls -1 "$BACKUP_DIR"/*.tar 2>/dev/null | wc -l)
    if [ "$COUNT" -gt 3 ]; then
        ls -t "$BACKUP_DIR"/*.tar | tail -n +4 | xargs rm -f
        echo "Removed $((COUNT - 3)) old backups, kept last 3"
    fi
fi

echo "[$(date)] Cleanup complete"
df -h / | tail -1
"""

print("\n=== Создание скрипта очистки ===")
# Write script
run("cat > /usr/local/bin/docker-cleanup.sh << 'SCRIPT'\n" + cleanup_script + "\nSCRIPT", 5)
run("chmod +x /usr/local/bin/docker-cleanup.sh", 5)
print(run("ls -la /usr/local/bin/docker-cleanup.sh", 5))

# Add cron job - weekly on Sunday at 3am
print("\n=== Добавление cron задачи (каждое воскресенье в 3:00) ===")
cron_cmd = '(crontab -l 2>/dev/null; echo "0 3 * * 0 /usr/local/bin/docker-cleanup.sh >> /var/log/docker-cleanup.log 2>&1") | crontab -'
print(run(cron_cmd, 5))

# Verify
print("\n=== Финальный crontab ===")
print(run("crontab -l 2>&1", 5))

# Also add Docker log rotation via daemon.json
print("\n=== Настройка Docker log rotation ===")
docker_daemon = run("cat /etc/docker/daemon.json 2>&1", 5)
if 'log-opts' not in docker_daemon:
    run("""cat > /etc/docker/daemon.json << 'EOF'
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
EOF""", 5)
    print("Docker daemon.json настроен на ротацию логов (10MB, 3 файла)")
    print("⚠️  Нужен перезапуск Docker: systemctl restart docker")
else:
    print(f"Уже настроен:\n{docker_daemon}")

# Test run the script
print("\n=== Тестовый запуск скрипта ===")
print(run("bash /usr/local/bin/docker-cleanup.sh 2>&1", 60))

print("\n=== Готово! ===")
ssh.close()
