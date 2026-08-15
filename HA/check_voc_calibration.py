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

print("=== voc() extend ===")
voc = run("docker exec big-bear-zigbee2mqtt grep -n -A 100 'voc: ()' /app/node_modules/.pnpm/zigbee-herdsman-converters@26.63.0/node_modules/zigbee-herdsman-converters/dist/lib/develco.js 2>&1 | head -80", 15)
print(voc)

print("\n=== Custom cluster definition ===")
custom = run("docker exec big-bear-zigbee2mqtt grep -n -A 40 'addCustomClusterManuSpecificDevelcoAirQuality' /app/node_modules/.pnpm/zigbee-herdsman-converters@26.63.0/node_modules/zigbee-herdsman-converters/dist/lib/develco.js 2>&1 | head -80", 15)
print(custom)

# Check for calibration attributes in the cluster
print("\n=== All attributes of manuSpecificDevelcoAirQuality ===")
attrs = run("docker exec big-bear-zigbee2mqtt grep -n -A 30 'manuSpecificDevelcoAirQuality' /app/node_modules/.pnpm/zigbee-herdsman-converters@26.63.0/node_modules/zigbee-herdsman-converters/dist/lib/develco.js 2>&1 | head -100", 15)
print(attrs)

# Also look for calibration in zigbee-herdsman zcl definition
print("\n=== ZCL definition for Develco cluster ===")
zcl = run("docker exec big-bear-zigbee2mqtt grep -rn 'DevelcoAirQuality\\|manuSpecificDevelco' /app/node_modules/.pnpm/zigbee-herdsman-converters@26.63.0/node_modules/zigbee-herdsman-converters/dist/ 2>&1 | head -20", 15)
print(zcl)

# Check if there's a zigbee-herdsman ZCL definition
zcl2 = run("docker exec big-bear-zigbee2mqtt grep -rn 'DevelcoAirQuality' /app/node_modules/.pnpm/zigbee-herdsman@*/node_modules/zigbee-herdsman/dist/ 2>&1 | head -10", 15)
print(f"\n=== ZCL (herdsman): {zcl2}")

# Check available exposes for MCLH-08 via MQTT
print("\n=== Полные exposes датчика ===")
exposes = run("mosquitto_sub -h localhost -p 1883 -u mqtt -P CHANGE_ME -t zigbee2mqtt/bridge/devices -C 1 -W 5 2>&1 | python3 -c \"import sys,json; d=json.loads(sys.stdin.read().split(' ',1)[1]); [print(json.dumps(x,indent=2)) for x in d if '00158d' in str(x)][0]\" 2>/dev/null || echo '(parse error)'", 15)
print(exposes[:2000])

ssh.close()
