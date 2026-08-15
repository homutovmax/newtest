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

# Check all exposes for the datchik device from Z2M bridge
print("=== Exposes MCLH-08 ===")
exposes = run("mosquitto_sub -h localhost -p 1883 -u mqtt -P CHANGE_ME -t zigbee2mqtt/bridge/devices -C 1 -W 5 2>&1 | python3 -c \"import sys,json; data=json.loads(sys.stdin.read().split(' ',1)[1]); [print(json.dumps(d.get('definition',{}).get('exposes',[]),indent=2)) for d in data if '00158d0000d9cd2c' in d.get('ieee_address','')]\" 2>/dev/null || echo '(parse error)'", 15)
print(exposes[:3000])

# Check if z2m has temperature calibration option
print("\n=== Поиск temperature_calibration в converters ===")
cal = run("docker exec big-bear-zigbee2mqtt grep -rn 'temperature_calibration\\|temperature_offset\\|temp_calibration' /app/node_modules/.pnpm/zigbee-herdsman-converters@26.63.0/node_modules/zigbee-herdsman-converters/dist/lib/ 2>&1 | head -10", 15)
print(cal if cal else '(нет стандартного offset для этого типа датчика)')

# Check what temperature precision/offset options exist for the temperature extend
print("\n=== temperature() extend options ===")
temp = run("docker exec big-bear-zigbee2mqtt grep -n -A 20 'temperature:.*=>' /app/node_modules/.pnpm/zigbee-herdsman-converters@26.63.0/node_modules/zigbee-herdsman-converters/dist/lib/develco.js 2>&1 | head -30", 15)
print(temp)

# Check the temperature modernExtend for calibration options
print("\n=== modernExtend temperature ===")
modtemp = run("grep -n -A 30 'function temperature' /app/node_modules/.pnpm/zigbee-herdsman-converters@26.63.0/node_modules/zigbee-herdsman-converters/dist/lib/modernExtend.js 2>/dev/null | head -40", 15)
if 'ERR' in modtemp:
    modtemp = run("docker exec big-bear-zigbee2mqtt grep -n -A 30 'function temperature' /app/node_modules/.pnpm/zigbee-herdsman-converters@26.63.0/node_modules/zigbee-herdsman-converters/dist/lib/modernExtend.js 2>&1 | head -40", 15)
print(modtemp[:2000])

ssh.close()
