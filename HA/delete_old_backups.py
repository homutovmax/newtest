import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=15)

def run(cmd, timeout=15):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    return stdout.read().decode('utf-8', errors='replace').strip()

# Keep only the latest backup (from June 22)
backup_dir = '/DATA/AppData/homeassistant/config/backups'
print("=== Текущие бекапы ===")
print(run(f"ls -lh {backup_dir}/ 2>&1", 5))

# Remove the two oldest backups
old_backups = [
    "Automatic_backup_2026.5.4_2026-06-18_05.12_26005159.tar",
    "Automatic_backup_2026.6.3_2026-06-21_05.42_55004181.tar"
]
for b in old_backups:
    result = run(f"rm -f {backup_dir}/{b} 2>&1 && echo 'DELETED' || echo 'FAILED'", 5)
    print(f"  {b}: {result}")

print("\n=== После очистки ===")
print(run(f"ls -lh {backup_dir}/ 2>&1", 5))

print("\n=== Диск после всех чисток ===")
print(run("df -h / 2>&1", 5))

ssh.close()
