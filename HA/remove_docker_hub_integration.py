import paramiko, json

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

TOKEN = "CHANGE_ME"

def delete_integration(domain_keyword, name):
    print(f"=== {name} ===")
    entries_raw = run("curl -s -H 'Authorization: Bearer " + TOKEN + "' http://localhost:8123/api/config/config_entries/entry 2>&1", 15)
    try:
        entries = json.loads(entries_raw)
        found = False
        for e in entries if isinstance(entries, list) else []:
            if domain_keyword in str(e).lower():
                entry_id = e.get('entry_id')
                domain = e.get('domain')
                print(f"  Entry ID: {entry_id}, domain: {domain}, state: {e.get('state')}")
                if entry_id:
                    del_result = run("curl -s -X DELETE -H 'Authorization: Bearer " + TOKEN + "' "
                        f"-H 'Content-Type: application/json' "
                        f"'http://localhost:8123/api/config/config_entries/entry/{entry_id}' 2>&1", 15)
                    print(f"  Удаление: {del_result}")
                    found = True
        if not found:
            print(f"  (не найдена)")
    except Exception as ex:
        print(f"  Error: {ex}")

delete_integration('docker', 'Docker Hub')
delete_integration('radio_browser', 'Radio Browser')

print("\n=== Проверка ===")
check = run("curl -s -H 'Authorization: Bearer " + TOKEN + "' http://localhost:8123/api/states 2>&1 | python3 -c \"import sys,json; d=json.load(sys.stdin); [print(s['entity_id'], '=', s['state']) for s in d if 'docker_hub' in s['entity_id'].lower() or 'radio_browser' in s['entity_id'].lower()]\" 2>/dev/null", 15)
print(check if check else "(все удалено)")

ssh.close()
