import paramiko

HOST = '192.168.1.92'
USER = 'root'
PASS = 'CHANGE_ME'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=10)

# Find airQuality function definition
stdin, stdout, stderr = ssh.exec_command(
    'docker exec big-bear-zigbee2mqtt grep -r "airQuality\|function airQuality\|const airQuality\|airQuality =" /app/node_modules/zigbee-herdsman-converters/dist/ 2>/dev/null | head -20',
    timeout=15)
print("=== airQuality references ===")
print(stdout.read().decode('utf-8', errors='replace').strip())

# Also search in the whole dist
stdin2, stdout2, stderr2 = ssh.exec_command(
    'docker exec big-bear-zigbee2mqtt grep -n "airQuality" /app/node_modules/.pnpm/zigbee-herdsman-converters@26.63.0/node_modules/zigbee-herdsman-converters/dist/lib/experimental.js 2>/dev/null | head -30',
    timeout=10)
print("\n=== airQuality in experimental.js ===")
print(stdout2.read().decode('utf-8', errors='replace').strip())

# Read the airQuality function
stdin3, stdout3, stderr3 = ssh.exec_command(
    "docker exec big-bear-zigbee2mqtt awk '/function airQuality/,/^}/' /app/node_modules/.pnpm/zigbee-herdsman-converters@26.63.0/node_modules/zigbee-herdsman-converters/dist/lib/experimental.js 2>/dev/null | head -100",
    timeout=10)
print("\n=== airQuality function ===")
print(stdout3.read().decode('utf-8', errors='replace').strip())

ssh.close()
