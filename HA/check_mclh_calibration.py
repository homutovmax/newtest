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

# Read the full MCLH-08 definition from Z2M lifecontrol.js
print("=== Полное определение MCLH-08 в Z2M ===")
definition = run("docker exec big-bear-zigbee2mqtt grep -A 30 'VOC_Sensor' /app/node_modules/.pnpm/zigbee-herdsman-converters@26.63.0/node_modules/zigbee-herdsman-converters/dist/devices/lifecontrol.js 2>&1 | head -40", 15)
print(definition)

# Read airQuality extend function - search for calibration related code
print("\n=== airQuality extend (develco.js) ===")
airq = run("grep -n -A 60 'airQuality:.*=>' /app/node_modules/.pnpm/zigbee-herdsman-converters@26.63.0/node_modules/zigbee-herdsman-converters/dist/lib/develco.js 2>/dev/null | head -80", 15)
# Need to run inside docker
airq2 = run("docker exec big-bear-zigbee2mqtt grep -n -A 80 'airQuality: ()' /app/node_modules/.pnpm/zigbee-herdsman-converters@26.63.0/node_modules/zigbee-herdsman-converters/dist/lib/develco.js 2>&1 | head -80", 15)
print(airq2)

# Check if there's a VOC extend with calibration
print("\n=== Поиск calibration в converters ===")
cal = run("docker exec big-bear-zigbee2mqtt grep -rn -i 'calibrat\\|calibr' /app/node_modules/.pnpm/zigbee-herdsman-converters@26.63.0/node_modules/zigbee-herdsman-converters/dist/lib/develco.js 2>&1 | head -20", 15)
print(cal if cal else '(нет)')

# Check available MQTT commands for this device
print("\n=== Доступные команды через MQTT ===")
# Try to get device info with available commands
cmds = run("mosquitto_sub -h localhost -p 1883 -u mqtt -P CHANGE_ME -t zigbee2mqtt/datchik_kachestva_vozdukha/availability -C 1 -W 3 2>&1", 10)
print(f"Availability: {cmds}")

# Check what topics exist for this device
print("\n=== Поиск calibration в Z2M логах ===")
logs = run("docker logs big-bear-zigbee2mqtt --tail 100 2>&1 | grep -iE 'calibrat|calibr'", 15)
print(logs if logs else '(нет упоминаний калибровки)')

# Check device specific configuration in Z2M
print("\n=== device-specific config ===")
devconf = run("docker exec big-bear-zigbee2mqtt grep -rn 'MCLH-08\\|VOC_Sensor' /app/node_modules/.pnpm/zigbee-herdsman-converters@26.63.0/node_modules/zigbee-herdsman-converters/dist/lib/ 2>&1 | head -20", 15)
print(devconf)

# Check manuSpecificDevelcoAirQuality cluster attributes
print("\n=== Develco air quality cluster ===")
manu = run("docker exec big-bear-zigbee2mqtt grep -rn 'manuSpecificDevelcoAirQuality\\|develcoAirQuality' /app/node_modules/.pnpm/zigbee-herdsman-converters@26.63.0/node_modules/zigbee-herdsman-converters/dist/ 2>&1 | head -20", 15)
print(manu)

ssh.close()
