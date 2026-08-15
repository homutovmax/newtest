import paramiko, time, json

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

for i in range(6):
    time.sleep(10)
    result = run('curl -s -H "Authorization: Bearer ' + TOKEN + '" http://localhost:8123/api/states 2>&1', 10)
    if result and 'air_conditioner' in result:
        try:
            data = json.loads(result)
            ac_entities = [e for e in data if 'air_conditioner' in e['entity_id']]
            if ac_entities:
                print(f"Attempt {i+1}: AC found ({len(ac_entities)} entities)")
                for e in ac_entities:
                    print(f"  {e['entity_id']} = {e['state']}")
                break
        except:
            print(f"Attempt {i+1}: JSON parse error")
    else:
        print(f"Attempt {i+1}: no AC yet")

# Check haier_evo logs
print()
logs = run("docker logs homeassistant --tail 100 2>&1 | grep -iE 'haier_evo|evo|iot' | tail -20", 15)
print(logs[:2000] if logs else '(no haier_evo logs)')

ssh.close()
