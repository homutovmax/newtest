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

# Read current daemon.json
print("=== Current daemon.json ===")
out = run("cat /etc/docker/daemon.json 2>/dev/null || echo 'FILE NOT FOUND'", 10)
print(out)

# Check current Docker DNS config
print("\n=== Docker daemon config ===")
out = run("docker info 2>/dev/null | grep -i -A2 'dns' | head -10", 10)
print(out[:500] if out else "(not found)")

# Check systemd DNS for Docker
print("\n=== Docker service DNS ===")
out = run("systemctl cat docker 2>/dev/null | grep -i dns | head -5", 10)
print(out[:500] if out else "(not found)")

# Check host DNS
print("\n=== Host DNS ===")
out = run("cat /etc/resolv.conf 2>/dev/null", 10)
print(out[:500])

# Test DNS speed
print("\n=== DNS speed test ===")
for dns in ['192.168.1.1', '1.1.1.1', '8.8.8.8', '77.88.8.8']:
    out = run(f"timeout 5 bash -c 'time (nslookup google.com {dns} 2>&1)' 2>&1 | grep -i real | tail -1", 10)
    print(f"  {dns}: {out[:100]}")

ssh.close()
