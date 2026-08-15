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

print("=== Все сенсоры температуры ===")
states = run("curl -s -H 'Authorization: Bearer " + TOKEN + "' http://localhost:8123/api/states 2>&1 | python3 -c \"import sys,json; d=json.load(sys.stdin); [print(s['entity_id'], '=', s['state']) for s in d if 'temperature' in s['entity_id'].lower() or 'temp' in s['entity_id'].lower()]\" 2>/dev/null", 15)
print(states)

print("\n=== Все сенсоры влажности (для контекста) ===")
states2 = run("curl -s -H 'Authorization: Bearer " + TOKEN + "' http://localhost:8123/api/states 2>&1 | python3 -c \"import sys,json; d=json.load(sys.stdin); [print(s['entity_id'], '=', s['state']) for s in d if 'humidity' in s['entity_id'].lower()]\" 2>/dev/null", 15)
print(states2)

# Check attributes of the datchik temperature sensor for precision/offset
print("\n=== Атрибуты datchik temperature ===")
attrs = run("curl -s -H 'Authorization: Bearer " + TOKEN + "' http://localhost:8123/api/states/sensor.datchik_kachestva_vozdukha_temperature 2>&1 | python3 -m json.tool 2>/dev/null", 15)
print(attrs[:1000])

# Check terrarium sensors too
print("\n=== Сравнение всех температур в одной комнате ===")
all_temps = run("curl -s -H 'Authorization: Bearer " + TOKEN + "' http://localhost:8123/api/states 2>&1 | python3 -c \"import sys,json; d=json.load(sys.stdin); [print(s['entity_id'], '=', s['state'], 'C | unit=', s['attributes'].get('unit_of_measurement','?')) for s in d if s['entity_id'].endswith('temperature') and s['state'] not in ['unavailable','unknown']]\" 2>/dev/null", 15)
print(all_temps)

ssh.close()
