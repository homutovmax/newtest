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

print("=== Device models ===")
models = run("docker exec unifi-controller mongo --port 27117 unifi --quiet --eval 'db.device.distinct(\"model\")' 2>&1", 15)
print(models)

print("\n=== Device names ===")
names = run("docker exec unifi-controller mongo --port 27117 unifi --quiet --eval 'db.device.distinct(\"name\")' 2>&1", 15)
print(names)

print("\n=== Device count ===")
count = run("docker exec unifi-controller mongo --port 27117 unifi --quiet --eval 'db.device.count()' 2>&1", 15)
print(f"Count: {count}")

print("\n=== All devices ===")
devices = run("docker exec unifi-controller mongo --port 27117 unifi --quiet --eval 'db.device.find({},{name:1,model:1,state:1,ip:1,adopted:1,_id:0}).forEach(function(d){print(JSON.stringify(d))})' 2>&1 | head -30", 15)
print(devices)

# Also check what keenetic shows
print("\n=== HA keenetic gateway ===")
TOKEN = "CHANGE_ME"
keenetic = run("curl -s -H 'Authorization: Bearer " + TOKEN + "' http://localhost:8123/api/states 2>&1 | python3 -c \"import sys,json; d=json.load(sys.stdin); [print(s['entity_id'], '=', s['state']) for s in d if 'keenetic' in s['entity_id'].lower() or 'gateway' in s['entity_id'].lower() or 'router' in s['entity_id'].lower()]\" 2>/dev/null", 15)
print(keenetic[:2000])

ssh.close()
