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

# Check if haier_evo has token files
print("=== Token files ===")
out = run("ls -la /DATA/AppData/homeassistant/config/haier_evo/ 2>/dev/null", 10)
print(out[:500] if out else "(not found)")

# Check current HA logs for haier connection attempts
print("\n=== Recent haier_evo logs ===")
out = run("docker logs homeassistant --tail 200 2>&1 | grep -iE 'haier_evo|evo\.haier|iot-platform|websocket|ws|conn' | tail -30", 15)
print(out[:3000] if out else "(none)")

# Try to force reload the integration via API
print("\n=== Try reload haier_evo ===")
out = run(f"curl -s -X POST -H 'Authorization: Bearer {TOKEN}' -H 'Content-Type: application/json' http://localhost:8123/api/config/config_entries/entry/01KNHTZYKTJZ0NNJS74SN5JPZ0/reload 2>&1", 10)
print(f"  reload: {out[:300]}")

# Check integration state after reload
import time
time.sleep(3)

# Check AC entity state
print("\n=== AC entity after reload ===")
cmd = 'curl -s -H "Authorization: Bearer ' + TOKEN + '" http://localhost:8123/api/states/climate.air_conditioner_as35hpl2hra 2>&1 | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get(\'state\',\'?\'), d.get(\'attributes\',{}).get(\'restored\',\'n/a\'))"'
out = run(cmd, 10)
print(f"  {out[:200]}")

# Check if we can test WS connection
print("\n=== Test WebSocket ===")
out = run("timeout 10 python3 -c \"import websocket; ws=websocket.create_connection('wss://iot-platform.evo.haieronline.ru/gateway-ws-service/ws/', timeout=10); print('Connected'); ws.close()\" 2>&1", 20)
print(f"  WS: {out[:300]}")

# Try WS from HA container
print("\n=== WS from HA ===")
out = run("docker exec homeassistant timeout 10 python3 -c \"import websocket; ws=websocket.create_connection('wss://iot-platform.evo.haieronline.ru/gateway-ws-service/ws/', timeout=10); print('Connected'); ws.close()\" 2>&1", 20)
print(f"  WS HA: {out[:300]}")

# Check recent logs more carefully for errors
print("\n=== ERROR logs ===")
out = run("docker logs homeassistant --tail 500 2>&1 | grep -iE 'error|exception|traceback|fail' | grep -ivE 'startup|stopping|deprecated|finish' | tail -20", 15)
print(out[:2000] if out else "(none)")

# Check all haier_evo entities state
print("\n=== All haier entities ===")
cmd = 'curl -s -H "Authorization: Bearer ' + TOKEN + '" http://localhost:8123/api/states 2>&1 | python3 -c "import sys,json; d=json.load(sys.stdin); [print(e[\'entity_id\'], e[\'state\']) for e in d if \'haier_evo\' in e[\'entity_id\'] or \'air_conditioner\' in e[\'entity_id\']]"'
out = run(cmd, 10)
print(out[:1000] if out else "(none)")

# Check if integration is loaded (check HA services)
print("\n=== HA services for haier ===")
cmd = 'curl -s -H "Authorization: Bearer ' + TOKEN + '" http://localhost:8123/api/services 2>&1 | python3 -c "import sys,json; d=json.load(sys.stdin); [print(s[\'domain\'], s[\'services\']) for s in d if \'haier\' in s[\'domain\']]"'
out = run(cmd, 10)
print(out[:500] if out else "(none)")

ssh.close()
