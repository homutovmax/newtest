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

TOKEN = "CHANGE_ME"

# Check config entries for haier/AC
print("=== AC config entries ===")
entries = run("curl -s -H 'Authorization: Bearer " + TOKEN + "' http://localhost:8123/api/config/config_entries/entry 2>&1 | python3 -c \"import sys,json; d=json.load(sys.stdin); [print(json.dumps(e,indent=2)) for e in (d if isinstance(d,list) else []) if 'haier' in str(e).lower() or 'air_conditioner' in str(e).lower() or 'ac' in str(e).lower()]\" 2>/dev/null", 15)
print(entries if entries else "(не найдено)")

# Check all AC entities
print("\n=== AC entities ===")
ac = run("curl -s -H 'Authorization: Bearer " + TOKEN + "' http://localhost:8123/api/states 2>&1 | python3 -c \"import sys,json; d=json.load(sys.stdin); [print(s['entity_id'], '=', s['state']) for s in d if 'air_conditioner' in s['entity_id'].lower()]\" 2>/dev/null", 15)
print(ac if ac else "(нет)")

# Check HA logs for AC errors
print("\n=== HA logs (AC errors) ===")
logs = run("docker logs homeassistant --tail 200 2>&1 | grep -iE 'air_conditioner|haier|as35|ac_' | tail -20", 15)
if logs and 'ERR' not in logs:
    try:
        cleaned = []
        for line in logs.split('\n'):
            try:
                cleaned.append(line.encode('cp1251', errors='replace').decode('cp1251'))
            except:
                pass
        print('\n'.join(cleaned) if cleaned else logs)
    except:
        print(logs[:2000])
else:
    print(logs[:500])

# Check haier_evo integration
print("\n=== haier_evo integration ===")
haier = run("docker exec homeassistant find /config -path '*haier*' -o -path '*haier_evo*' 2>/dev/null | head -20", 15)
print(haier if haier else "(нет файлов haier)")

# Check custom_components
print("\n=== custom_components ===")
comps = run("docker exec homeassistant ls /config/custom_components/ 2>/dev/null", 10)
print(comps if comps else "(нет custom_components)")

# Check network connectivity to Haier cloud
print("\n=== Ping/curl to Haier cloud ===")
dns = run("nslookup haieriot.com 2>&1 | head -5", 10)
print(f"DNS haieriot.com: {dns.split(chr(10))[3] if len(dns.split(chr(10)))>3 else dns[:200]}")

curl = run("curl -s -o /dev/null -w '%{http_code}' --connect-timeout 5 https://haieriot.com/ 2>&1", 10)
print(f"HTTPS haieriot.com: {curl}")

curl2 = run("curl -s -o /dev/null -w '%{http_code}' --connect-timeout 5 http://haieriot.com/ 2>&1", 10)
print(f"HTTP haieriot.com: {curl2}")

# From HA container
print("\n=== Из HA контейнера ===")
ha_curl = run("docker exec homeassistant curl -s -o /dev/null -w '%{http_code}' --connect-timeout 10 https://haieriot.com/ 2>&1", 15)
print(f"HA -> haieriot.com: {ha_curl}")

ssh.close()
