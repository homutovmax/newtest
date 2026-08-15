import paramiko, re

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=15)

def run(cmd, timeout=15):
    try:
        stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
        return stdout.read().decode('utf-8', errors='replace').strip()
    except Exception as e:
        return f'ERR: {e}'

TOKEN = "CHANGE_ME"

# Check actual API endpoints
print("=== Real API endpoints ===")
for url in ['https://evo.haieronline.ru',
            'https://iot-platform.evo.haieronline.ru',
            'https://evo.haieronline.ru/v2/ru/users/auth/sign-in']:
    out = run(f"curl -s -o /dev/null -w '%{{http_code}}' --connect-timeout 10 '{url}' 2>&1", 15)
    print(f"  {url}: {out}")

# DNS resolution for real endpoints
print("\n=== DNS for real endpoints ===")
for d in ['evo.haieronline.ru', 'iot-platform.evo.haieronline.ru']:
    out = run(f"nslookup {d} 2>&1 | tail -5", 10)
    print(f"  {d}: {out[:200]}")

# Check HA logs for haier_evo errors
print("\n=== HA logs haier_evo ===")
logs = run("docker logs homeassistant --tail 500 2>&1 | grep -i 'haier_evo\|haier' | tail -40", 15)
print(logs[:5000] if logs else "(no logs)")

# Check if login works from HA container
print("\n=== Test login from HA ===")
ha = run("docker exec homeassistant python3 -c \"import requests; r=requests.post('https://evo.haieronline.ru/v2/ru/users/auth/sign-in', json={}, timeout=15); print(r.status_code, r.text[:500])\" 2>&1", 20)
print(f"  {ha[:500]}")

# Get full haier_evo integration details from HA API
print("\n=== haier_evo state info ===")
info = run("curl -s -H 'Authorization: Bearer " + TOKEN + "' http://localhost:8123/api/config/config_entries/entry/01KNHTZYKTJZ0NNJS74SN5JPZ0 2>&1 | python3 -c \"import sys,json; d=json.load(sys.stdin); print(json.dumps(d, indent=2, ensure_ascii=False))\" 2>/dev/null", 10)
print(info[:2000] if info else "(not found)")

# Check climate entity attributes
print("\n=== AC climate attributes ===")
attrs = run("curl -s -H 'Authorization: Bearer " + TOKEN + "' http://localhost:8123/api/states/climate.air_conditioner_as35hpl2hra 2>&1 | python3 -c \"import sys,json; d=json.load(sys.stdin); print(json.dumps(d, indent=2, ensure_ascii=False))\" 2>/dev/null", 10)
print(attrs[:2000] if attrs else "(not found)")

# Check if hacs has any updates for haier_evo
print("\n=== HACS info ===")
hacs = run("curl -s -H 'Authorization: Bearer " + TOKEN + "' http://localhost:8123/api/hacs/repository?repository=haier_evo 2>&1 | python3 -c \"import sys,json; d=json.load(sys.stdin); print(d.get('installed_version','unknown'), '->', d.get('available_version','unknown'))\" 2>/dev/null", 10)
print(f"  haier_evo version: {hacs}")

# More HA logs
print("\n=== All error logs ===")
errs = run("docker logs homeassistant --tail 1000 2>&1 | grep -i 'error\|exception\|traceback\|fail\|unavailable' | grep -i 'haier\|evo\|climate\|air_conditioner' | tail -20", 15)
print(errs[:3000] if errs else "(none)")

ssh.close()
