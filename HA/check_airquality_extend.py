import paramiko

HOST = '192.168.1.92'
USER = 'root'
PASS = 'CHANGE_ME'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=10)

# Read the airQuality function from develco.js
stdin, stdout, stderr = ssh.exec_command(
    "docker exec big-bear-zigbee2mqtt awk '/airQuality:.*=>/,/^    },\\n    \\/[/*]/' /app/node_modules/.pnpm/zigbee-herdsman-converters@26.63.0/node_modules/zigbee-herdsman-converters/dist/lib/develco.js 2>/dev/null | head -150",
    timeout=10)
print("=== airQuality extend in develco.js ===")
print(stdout.read().decode('utf-8', errors='replace').strip())

# Also search for airQuality in all lib files for reporting config
stdin2, stdout2, stderr2 = ssh.exec_command(
    "docker exec big-bear-zigbee2mqtt grep -n -A5 -B2 'airQuality' /app/node_modules/.pnpm/zigbee-herdsman-converters@26.63.0/node_modules/zigbee-herdsman-converters/dist/lib/develco.js 2>/dev/null | head -80",
    timeout=10)
print("\n=== airQuality in develco.js (context) ===")
print(stdout2.read().decode('utf-8', errors='replace').strip())

ssh.close()
