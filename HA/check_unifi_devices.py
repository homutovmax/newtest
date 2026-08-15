import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=15)

def run(cmd, timeout=10):
    try:
        stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
        return stdout.read().decode('utf-8', errors='replace').strip()
    except Exception as e:
        return f'ERR: {e}'

# Check devices in unifi controller via internal API  
print("=== Устройства UniFi (через MongoDB) ===")
# Try to access the unifi controller's MongoDB for device info
devices = run("docker exec unifi-controller mongo --port 27117 --authenticationDatabase admin -u root -p '' --eval 'db.serverStatus()' 2>&1 | head -5", 10)
print(devices)

# Check logs for device connections
print("\n=== Недавние подключения устройств ===")
logs = run("docker logs unifi-controller --tail 100 2>&1 | grep -iE 'adopt|device|discover|connect|inform|UAP|USW|UGW|uap_|usw_' | tail -20", 15)
if logs and 'ERR' not in logs:
    # Filter only printable lines
    clean = []
    for line in logs.split('\n'):
        try:
            line.encode('cp1251')
            clean.append(line)
        except:
            pass
    print('\n'.join(clean) if clean else '(нет читаемых строк)')
else:
    print('(нет данных о подключениях)' if 'ERR' in logs else logs)

# Check if unifi has any configured devices via the web API
print("\n=== Статистика UniFi ===")
stats = run("docker exec unifi-controller unifi-api -k -q '{\"cmd\":\"get-aps\"}' 2>&1 | head -30", 10)
print(stats)

# Check port 8080 for inform data
print("\n=== Информация о коллекторе ===")
print(run('ss -tlnp 2>/dev/null | grep 8080', 5))

# Check if the keenetic gateway is the router with unifi
print("\n=== Сетевые устройства в HA ===")
TOKEN = "CHANGE_ME"
devices_ha = run("curl -s -H 'Authorization: Bearer " + TOKEN + "' http://localhost:8123/api/states 2>&1 | python3 -c \"import sys,json; d=json.load(sys.stdin); [print(s['entity_id'], '=', s['state']) for s in d if 'unifi' in s['entity_id'].lower()]\" 2>/dev/null", 15)
print(devices_ha if devices_ha else "(нет устройств unifi в HA)")

ssh.close()
