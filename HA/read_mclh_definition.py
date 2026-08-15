import paramiko, json

HOST = '192.168.1.92'
USER = 'root'
PASS = 'CHANGE_ME'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=10)

# Read the lifecontrol.js device definition
stdin, stdout, stderr = ssh.exec_command(
    'docker exec big-bear-zigbee2mqtt cat /app/node_modules/.pnpm/zigbee-herdsman-converters@26.63.0/node_modules/zigbee-herdsman-converters/dist/devices/lifecontrol.js 2>&1',
    timeout=10)
content = stdout.read().decode('utf-8', errors='replace')

# Find MCLH-08 section
if 'MCLH-08' in content:
    start = content.find('MCLH-08')
    # Go back to find the beginning of this device definition
    section_start = content.rfind('{', 0, start)
    # Go forward past several lines
    section_end = content.find('},', start)
    if section_end < 0:
        section_end = content.find('});', start)
    if section_end < 0:
        section_end = start + 2000
    print(f"MCLH-08 definition:\n{content[max(0,section_start-100):section_end+100]}")
else:
    # Search for VOC_Sensor or Nexturn
    for kw in ['VOC_Sensor', 'Nexturn', '00158d', 'air quality']:
        idx = content.lower().find(kw.lower())
        if idx >= 0:
            start = max(0, idx - 200)
            end = min(len(content), idx + 1000)
            print(f"Found '{kw}' at position {idx}:\n{content[start:end]}")
            print("---")

ssh.close()
