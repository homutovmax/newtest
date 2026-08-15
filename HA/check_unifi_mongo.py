import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=15)

def run(cmd, timeout=10):
    try:
        stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
        return stdout.read().decode('utf-8', errors='replace')
    except Exception as e:
        return f'ERR: {e}'

# Find unifi mongodb credentials
print("=== Поиск конфига UniFi ===")
config = run("cat /DATA/AppData/unifi-controller/data/system.properties 2>/dev/null | grep -v '^#' | grep -v '^$'", 10)
print(config[:2000] if config else "(нет файла)")

# Check if unifi has devices configured via the MongoDB unifi db
print("\n=== Устройства из MongoDB (ace.device) ===")
# Default unifi mongo creds: db=unifi, collection=device
devices = run("docker exec unifi-controller mongo unifi --quiet --eval 'db.device.find({}, {name:1, model:1, type:1, state:1, ip:1, _id:0}).forEach(printjson)' 2>&1 | head -40", 15)
print(devices[:3000] if devices else "(нет доступа)")

# Try with ace collection
print("\n=== Попытка через ace DB ===")
devices2 = run("docker exec unifi-controller mongo ace --quiet --eval 'db.device.find({}, {name:1, model:1, type:1, state:1, ip:1, _id:0}).forEach(printjson)' 2>&1 | head -40", 15)
print(devices2[:3000] if devices2 else "(нет доступа)")

# Just check the data directory
print("\n=== UniFi data directory ===")
print(run("ls -la /DATA/AppData/unifi-controller/data/ 2>/dev/null | head -20", 5))

# Access logs for device adoption
print("\n=== UniFi log for adoptions ===")
logs = run("docker logs unifi-controller --tail 200 2>&1", 15)
# Filter for device-related lines, handling encoding
import re
for line in logs.split('\n'):
    if re.search(r'adopt|device|inform|UAP[ -]|USW[ -]|UGW[ -]|UniFi', line, re.IGNORECASE):
        try:
            print(line)
        except:
            pass

ssh.close()
