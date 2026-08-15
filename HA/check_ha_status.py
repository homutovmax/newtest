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

print("=== HA контейнер ===")
print(run("docker ps --filter name=homeassistant --format '{{.Names}} {{.Status}} {{.Size}}'", 5))

print("\n=== HA API ===")
ha_status = run("curl -s -o /dev/null -w '%{http_code}' http://localhost:8123/api/ 2>&1", 5)
print(f"HTTP status: {ha_status}")

print("\n=== HA version ===")
TOKEN = "CHANGE_ME"
ver = run("curl -s -H 'Authorization: Bearer " + TOKEN + "' http://localhost:8123/api/config 2>&1 | python3 -c \"import sys,json; d=json.load(sys.stdin); print(d.get('version','?'))\" 2>/dev/null", 10)
print(f"Version: {ver}")

print("\n=== Datchik entities ===")
states = run("curl -s -H 'Authorization: Bearer " + TOKEN + "' http://localhost:8123/api/states 2>&1 | python3 -c \"import sys,json; d=json.load(sys.stdin); [print(s['entity_id'], '=', s['state']) for s in d if 'datchik' in s['entity_id'].lower()]\" 2>/dev/null", 15)
print(states)

print("\n=== Z2M MCLH-08 ===")
dev = run("mosquitto_sub -h localhost -p 1883 -u mqtt -P CHANGE_ME -t zigbee2mqtt/bridge/devices -C 1 -W 5 2>&1 | grep -o '\"friendly_name\":\"[^\"]*\"[^}]*\"ieee_address\":\"0x00158d0000d9cd2c\"[^}]*' 2>&1", 10)
print(dev)

print("\n=== Все контейнеры ===")
print(run("docker ps --format 'table {{.Names}}\t{{.Status}}' 2>&1", 5))

print("\n=== Последние логи HA (ошибки) ===")
errs = run("docker logs homeassistant --tail 30 2>&1 | grep -iE 'error|warn|fail|mqtt|datchik' | tail -10", 10)
print(errs if errs else "(нет ошибок)")

ssh.close()
