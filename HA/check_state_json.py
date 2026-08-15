import paramiko, json

HOST = '192.168.1.92'
USER = 'root'
PASS = 'CHANGE_ME'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=10)

sftp = ssh.open_sftp()

# Read state.json
print("=== state.json FULL CONTENT ===")
with sftp.open('/DATA/AppData/big-bear-zigbee2mqtt/data/state.json', 'r') as f:
    content = f.read().decode('utf-8')
    state = json.loads(content)
    print(json.dumps(state, indent=2, ensure_ascii=False)[:5000])

# Read configuration.yaml
print("\n=== Z2M configuration.yaml ===")
try:
    with sftp.open('/DATA/AppData/big-bear-zigbee2mqtt/data/configuration.yaml', 'r') as f:
        print(f.read().decode('utf-8')[:3000])
except:
    print("Could not read configuration.yaml")

# Check database.db - devices table
print("\n=== Z2M database devices ===")
stdin, stdout, stderr = ssh.exec_command(
    'sqlite3 /DATA/AppData/big-bear-zigbee2mqtt/data/database.db ".tables" 2>&1',
    timeout=10)
print(f"Tables: {stdout.read().decode('utf-8', errors='replace').strip()}")

# Check device table schema
stdin2, stdout2, stderr2 = ssh.exec_command(
    'sqlite3 /DATA/AppData/big-bear-zigbee2mqtt/data/database.db ".schema device" 2>&1',
    timeout=10)
print(f"Device schema: {stdout2.read().decode('utf-8', errors='replace').strip()}")

# Find MCLH-08 in database
stdin3, stdout3, stderr3 = ssh.exec_command(
    'sqlite3 /DATA/AppData/big-bear-zigbee2mqtt/data/database.db "SELECT * FROM device WHERE ieee_address LIKE \'%00158d%\' OR friendly_name LIKE \'%MCLH%\' OR model LIKE \'%MCLH%\';" 2>&1',
    timeout=10)
print(f"MCLH-08 in DB: {stdout3.read().decode('utf-8', errors='replace').strip()}")

# List all devices
stdin4, stdout4, stderr4 = ssh.exec_command(
    "sqlite3 /DATA/AppData/big-bear-zigbee2mqtt/data/database.db \"SELECT ieee_address, friendly_name, model, manufacturer FROM device;\" 2>&1",
    timeout=10)
print(f"\nAll devices in DB:")
print(stdout4.read().decode('utf-8', errors='replace').strip())

sftp.close()
ssh.close()
