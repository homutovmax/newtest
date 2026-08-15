import paramiko, json, re

HOST = '192.168.1.92'
USER = 'root'
PASS = 'CHANGE_ME'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=10)

# Get Z2M logs with errors
stdin, stdout, stderr = ssh.exec_command(
    'docker logs big-bear-zigbee2mqtt --tail 100 2>&1',
    timeout=15)
z2m_logs = stdout.read().decode('utf-8', errors='replace')
print('=== Z2M LOGS (last 100 lines, errors/warnings/MCLH) ===')
for line in z2m_logs.split('\n'):
    lower = line.lower()
    if any(kw in lower for kw in ['error', 'warn', 'mclh', '00158d', 'fail', 'interview', 'datchik']):
        print(line)

# Get all Z2M devices info
stdin2, stdout2, stderr2 = ssh.exec_command(
    'mosquitto_sub -h localhost -p 1883 -u mqtt -P CHANGE_ME '
    '-t zigbee2mqtt/bridge/devices -C 1 -W 5 -v 2>&1',
    timeout=15)
z2m_raw = stdout2.read().decode('utf-8', errors='replace').strip()

# Parse device entries
print('\n=== ALL Z2M DEVICES ===')
devices = re.findall(
    r'\{[^}]*?"friendly_name":"([^"]+)"[^}]*?"ieee_address":"([^"]+)"[^}]*?"interview_completed":(true|false)[^}]*?"interview_state":"([^"]*)"[^}]*?\}',
    z2m_raw)
for friendly, ieee, completed, state in devices:
    print(f'  friendly: "{friendly}"  ieee: {ieee}  interview: {completed}  state: {state}')

# Also get MCLH device full info
mclh_start = z2m_raw.find('0x00158d0000d9cd2c')
if mclh_start >= 0:
    bracket_start = z2m_raw.rfind('{', 0, mclh_start)
    bracket_end = z2m_raw.find('}', mclh_start)
    if bracket_start >= 0 and bracket_end > bracket_start:
        mclh_info = z2m_raw[bracket_start:bracket_end+1]
        print(f'\n=== MCLH-08 FULL DEVICE INFO ===')
        print(mclh_info)

# Check what topics the MCLH device publishes to
print('\n=== MCLH-08 MQTT TOPICS ===')
stdin3, stdout3, stderr3 = ssh.exec_command(
    'mosquitto_sub -h localhost -p 1883 -u mqtt -P CHANGE_ME '
    '-t zigbee2mqtt/0x00158d0000d9cd2c/# -C 1 -W 3 -v 2>&1',
    timeout=10)
topic_out = stdout3.read().decode('utf-8', errors='replace').strip()
if topic_out:
    print(topic_out)
else:
    print('(no messages on device topic)')

ssh.close()
