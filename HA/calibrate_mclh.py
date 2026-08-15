import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=15)

def run(cmd, timeout=15):
    try:
        stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
        return stdout.read().decode('utf-8', errors='replace').strip()
    except Exception as e:
        return f'ERR: {e}'

print("=== Текущие показания датчика ===")
data = run("mosquitto_sub -h localhost -p 1883 -u mqtt -P CHANGE_ME -t zigbee2mqtt/datchik_kachestva_vozdukha -C 1 -W 15 -v 2>&1", 20)
print(data)

# Try to send a calibration reset via ZCL
# The device uses manuSpecificDevelcoAirQuality cluster (0xFC03)
# Writing 0 to measuredValue may trigger recalibration
print("\n=== Сброс калибровки VOC ===")
# Send write to cluster 0xFC03 attribute 0x0000 (measuredValue) with value 0
run("mosquitto_pub -h localhost -p 1883 -u mqtt -P CHANGE_ME -t zigbee2mqtt/datchik_kachestva_vozdukha/set -m '{\"measured_value\": 0}' 2>&1", 5)
time.sleep(3)
print("Команда отправлена (write measuredValue=0)")

# Alternative: try writing to device via ZCL attribute write
run("mosquitto_pub -h localhost -p 1883 -u mqtt -P CHANGE_ME -t zigbee2mqtt/datchik_kachestva_vozdukha/write -m '{\"manuSpecificDevelcoAirQuality\": {\"measuredValue\": 0}}' 2>&1", 5)
time.sleep(3)
print("Команда write отправлена")

# Wait and check new values
print("\n=== Ожидание обновления (15 сек) ===")
time.sleep(15)

print("\n=== Новые показания ===")
data2 = run("mosquitto_sub -h localhost -p 1883 -u mqtt -P CHANGE_ME -t zigbee2mqtt/datchik_kachestva_vozdukha -C 1 -W 15 -v 2>&1", 20)
print(data2)

# Also check via HA API
TOKEN = "CHANGE_ME"
print("\n=== HA датчики ===")
states = run("curl -s -H 'Authorization: Bearer " + TOKEN + "' http://localhost:8123/api/states 2>&1 | python3 -c \"import sys,json; d=json.load(sys.stdin); [print(s['entity_id'], '=', s['state']) for s in d if 'datchik' in s['entity_id'].lower()]\" 2>/dev/null", 15)
print(states)

ssh.close()
