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

# Check radio_browser config entries
print("=== Radio Browser config entry ===")
entries = run("curl -s -H 'Authorization: Bearer " + TOKEN + "' http://localhost:8123/api/config/config_entries/entry 2>&1 | python3 -c \"import sys,json; d=json.load(sys.stdin); [print(json.dumps(e,indent=2)) for e in (d if isinstance(d,list) else []) if 'radio' in str(e).lower() or 'browser' in str(e).lower()]\" 2>/dev/null", 15)
print(entries if entries else "(не найдено)")

# Check radio entities
print("\n=== Radio entities ===")
states = run("curl -s -H 'Authorization: Bearer " + TOKEN + "' http://localhost:8123/api/states 2>&1 | python3 -c \"import sys,json; d=json.load(sys.stdin); [print(s['entity_id'], '=', s['state']) for s in d if 'radio' in s['entity_id'].lower()]\" 2>/dev/null", 15)
print(states if states else "(нет radio entities)")

# Check HA logs for radio errors
print("\n=== HA logs (radio errors) ===")
logs = run("docker logs homeassistant --tail 100 2>&1 | grep -iE 'radio|browser|media_player' | tail -20", 15)
if logs and 'ERR' not in logs:
    try:
        print(logs.encode('cp1251', errors='replace').decode('cp1251'))
    except:
        print(logs[:2000])
else:
    print(logs[:500])

# Check media_player entities (radio is usually played through media_player)
print("\n=== Media player entities ===")
players = run("curl -s -H 'Authorization: Bearer " + TOKEN + "' http://localhost:8123/api/states 2>&1 | python3 -c \"import sys,json; d=json.load(sys.stdin); [print(s['entity_id'], '=', s['state']) for s in d if 'media_player' in s['entity_id'].lower()]\" 2>/dev/null", 15)
print(players if players else "(нет)")

# Check internet access to radio browser API
print("\n=== Доступ к Radio Browser API ===")
api_check = run("curl -s -o /dev/null -w '%{http_code}' --connect-timeout 5 https://de1.api.radio-browser.info/ 2>&1", 10)
print(f"de1: {api_check}")

api_check2 = run("curl -s -o /dev/null -w '%{http_code}' --connect-timeout 5 https://at1.api.radio-browser.info/ 2>&1", 10)
print(f"at1: {api_check2}")

api_check3 = run("curl -s -o /dev/null -w '%{http_code}' --connect-timeout 5 http://de1.api.radio-browser.info/ 2>&1", 10)
print(f"de1 (http): {api_check3}")

# Check from HA container
print("\n=== Из HA контейнера ===")
ha_check = run("docker exec homeassistant curl -s -o /dev/null -w '%{http_code}' --connect-timeout 10 https://de1.api.radio-browser.info/ 2>&1", 15)
print(f"HA -> de1: {ha_check}")

ha_check2 = run("docker exec homeassistant curl -s -o /dev/null -w '%{http_code}' --connect-timeout 10 http://de1.api.radio-browser.info/ 2>&1", 15)
print(f"HA -> de1 (http): {ha_check2}")

ssh.close()
