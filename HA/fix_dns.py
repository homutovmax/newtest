import paramiko, json, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=15)

def run(cmd, timeout=30):
    try:
        stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
        return stdout.read().decode('utf-8', errors='replace').strip()
    except Exception as e:
        return f'ERR: {e}'

# Read current daemon.json
out = run("cat /etc/docker/daemon.json 2>/dev/null")
config = json.loads(out) if out else {}

# Add DNS config
config['dns'] = ['1.1.1.1', '8.8.8.8']

# Write updated config
new_config = json.dumps(config, indent=2)
print("=== New daemon.json ===")
print(new_config)

# Write via heredoc to avoid escaping issues
run(f"cat > /etc/docker/daemon.json << 'EOF'\n{new_config}\nEOF")
print("\n=== Config written ===")

# Verify
out = run("cat /etc/docker/daemon.json", 10)
print(out)

# Restart Docker daemon
print("\n=== Restarting Docker daemon ===")
out = run("systemctl restart docker 2>&1", 60)
print(out[:500] if out else "(ok)")

time.sleep(10)

# Check Docker is running
out = run("systemctl is-active docker 2>&1", 10)
print(f"Docker status: {out}")

# Check running containers after restart
out = run("docker ps --format '{{.Names}} {{.Status}}' 2>&1", 15)
print(f"Containers:\n{out}")

# Check HA container DNS
out = run("docker exec homeassistant cat /etc/resolv.conf 2>&1", 10)
print(f"\nHA resolv.conf:\n{out}")

# Test DNS from HA
out = run("docker exec homeassistant nslookup google.com 2>&1 | tail -5", 10)
print(f"\nDNS test from HA: {out[:200]}")

# Test problem domains
print("\n=== Problem domains from HA ===")
for d in ['my.zont.online', 'alerts.home-assistant.io', 'aa015h6buqvih86i1.api.met.no']:
    out = run(f"docker exec homeassistant nslookup {d} 2>&1 | tail -3", 10)
    print(f"  {d}: {out[:200]}")

# Wait for HA to start fully
print("\n=== Wait for HA to become responsive ===")
TOKEN = "CHANGE_ME"
for i in range(12):
    out = run(f"curl -s -o /dev/null -w '%{{http_code}}' -H 'Authorization: Bearer {TOKEN}' http://localhost:8123/api/ 2>&1", 10)
    if '200' in out or '201' in out:
        print(f"  HA ready after {i*10}s")
        break
    print(f"  Waiting... ({i*10}s)")
    time.sleep(10)

# Check AC state
print("\n=== AC state ===")
out = run(f"curl -s -H 'Authorization: Bearer {TOKEN}' http://localhost:8123/api/states/climate.air_conditioner_as35hpl2hra 2>&1 | python3 -c \"import sys,json; d=json.load(sys.stdin); print(d.get('state','?'))\"", 10)
print(f"  AC: {out[:100]}")

# Check haier_evo entities
print("\n=== Haier entities ===")
out = run(f"curl -s -H 'Authorization: Bearer {TOKEN}' http://localhost:8123/api/states 2>&1 | python3 -c \"import sys,json; d=json.load(sys.stdin); [print(e['entity_id'], '=', e['state']) for e in d if 'air_conditioner' in e['entity_id']]\"", 10)
print(out[:1000] if out else "(none)")

ssh.close()
