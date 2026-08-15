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

# Try specific endpoints on iot-platform
print("=== iot-platform specific endpoints ===")
# Try root first with more detail
out = run("curl -v --connect-timeout 10 https://iot-platform.evo.haieronline.ru/ 2>&1 | head -30", 15)
print(f"  root: {out[:1000]}")

# Try with explicit port 443
out = run("curl -s -o /dev/null -w '%{http_code}' --connect-timeout 10 https://iot-platform.evo.haieronline.ru:443/ 2>&1", 15)
print(f"  port 443: {out[:200]}")

# Try just the IP directly
out = run("curl -s -o /dev/null -w '%{http_code}' --connect-timeout 10 https://51.250.106.57/ -H 'Host: iot-platform.evo.haieronline.ru' 2>&1", 15)
print(f"  direct IP: {out[:200]}")

# TCP check
out = run("timeout 10 bash -c 'echo >/dev/tcp/51.250.106.57/443 && echo OK || echo FAIL' 2>&1", 15)
print(f"  TCP 443: {out[:200]}")

# Check ping
out = run("ping -c 2 -W 5 51.250.106.57 2>&1 | tail -3", 15)
print(f"  ping: {out[:200]}")

# Check the actual status API with MAC from config
print("\n=== Device status API ===")
# MAC from logs: 08:a6:f7:82:81:14
mac = "08A6F7828114"
out = run(f"curl -s -o /dev/null -w '%{{http_code}}' --connect-timeout 10 'https://iot-platform.evo.haieronline.ru/mobile-backend-service/api/v1/config/{mac}?type=DETAILED' 2>&1", 15)
print(f"  status API (no auth): {out[:200]}")

# Check from HA container
out = run("docker exec homeassistant curl -s -o /dev/null -w '%{http_code}' --connect-timeout 10 https://iot-platform.evo.haieronline.ru/ 2>&1", 15)
print(f"\n  HA -> iot-platform: {out[:200]}")

# Check if WS port is accessible
out = run("timeout 10 bash -c 'echo >/dev/tcp/51.250.106.57/80 && echo OK || echo FAIL' 2>&1", 15)
print(f"  TCP 80: {out[:200]}")

# Full HA logs for haier
print("\n=== Full haier_evo logs ===")
out = run("docker logs homeassistant 2>&1 | grep -A2 -B2 -i 'haier_evo\|evo\|iot-platform' | tail -60", 15)
print(out[:3000] if out else "(none)")

# Check what's happening with the websocket connection
print("\n=== WS test ===")
out = run("timeout 10 python3 -c \"import socket; s=socket.socket(); s.settimeout(10); s.connect(('51.250.106.57',443)); print('TCP 443 OK'); s.close()\" 2>&1", 15)
print(f"  TCP 443 via python: {out[:200]}")

# Check traceroute
out = run("traceroute -n -m 5 51.250.106.57 2>&1 | head -10", 15)
print(f"\n  traceroute:")
for l in out.split('\n')[:10]:
    print(f"    {l}")

ssh.close()
