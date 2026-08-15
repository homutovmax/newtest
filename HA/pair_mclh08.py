import paramiko
import json
import time
import sys
import threading
import re

HOST = '192.168.1.92'
USER = 'root'
PASS = 'CHANGE_ME'
MQTT_HOST = HOST
MQTT_PORT = 1883
MQTT_USER = 'mqtt'
MQTT_PASS = 'CHANGE_ME'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
print("Connecting to server...")
ssh.connect(HOST, username=USER, password=PASS, timeout=10)
print("Connected.")

def run(cmd, timeout=10):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    exit_code = stdout.channel.recv_exit_status()
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    return out, err, exit_code

def run_mqtt(topic, payload):
    cmd = f'mosquitto_pub -h {MQTT_HOST} -p {MQTT_PORT} -u "{MQTT_USER}" -P "{MQTT_PASS}" -t "{topic}" -m \'{json.dumps(payload)}\''
    return run(cmd)

def sub_mqtt(topic, count=1, timeout=15):
    cmd = f'mosquitto_sub -h {MQTT_HOST} -p {MQTT_PORT} -u "{MQTT_USER}" -P "{MQTT_PASS}" -t "{topic}" -C {count} -W {timeout} -v 2>&1'
    return run(cmd, timeout=timeout+5)

# Step 0: Check z2m and mosquitto
print("\n=== Checking services ===")
out, _, _ = run("docker ps --filter name=zigbee2mqtt --format '{{.Names}} {{.Status}}'")
print(f"z2m container: {out or 'NOT FOUND!'}")

out, _, _ = run("which mosquitto_pub")
print(f"mosquitto_pub: {out or 'NOT FOUND!'}")

out, _, _ = run("which mosquitto_sub")
print(f"mosquitto_sub: {out or 'NOT FOUND!'}")

# Step 1: Enable Permit Join
print("\n=== Enabling Permit Join (254s) ===")
out, err, code = run_mqtt('zigbee2mqtt/bridge/request/permit_join', {"time": 254})
print(f"Result: {out or err}")

# Verify
time.sleep(1)
out, err, _ = sub_mqtt('zigbee2mqtt/bridge/response/permit_join', count=1, timeout=5)
print(f"Response: {out or err}")

# Step 2: Monitor logs
print("\n=== Starting log monitor ===")
log_stdin, log_stdout, log_stderr = ssh.exec_command(
    f'mosquitto_sub -h {MQTT_HOST} -p {MQTT_PORT} -u "{MQTT_USER}" -P "{MQTT_PASS}" -t "zigbee2mqtt/bridge/logging" -t "zigbee2mqtt/bridge/event" -t "zigbee2mqtt/+/+" -v',
    timeout=120
)

log_thread_active = True
device_detected = threading.Event()
device_info = {}

def monitor_logs():
    global log_thread_active, device_info
    while log_thread_active:
        if log_stdout.channel.recv_ready():
            line = log_stdout.channel.recv(4096).decode('utf-8', errors='replace')
            if 'device_joined' in line or 'device_announce' in line:
                print(f"\n>>> {line.strip()}")
                device_detected.set()
            elif 'interview' in line:
                print(f"\n>>> {line.strip()}")
            elif 'permit_join' in line.lower():
                print(f">>> {line.strip()}")
            else:
                print(line.strip(), flush=True)
    print("Log monitor stopped.")

log_monitor = threading.Thread(target=monitor_logs, daemon=True)
log_monitor.start()

print("\n=== Ready! Press and hold the button on MCLH-08 for 5-7 sec ===")
print("=== LED should start blinking → release → short press ===")
print()
print("Type 'done' and press Enter when you've reset the device.")
print("Type 'skip' to continue without waiting.")

waiting = True
while waiting:
    try:
        cmd = input("> ").strip().lower()
        if cmd == 'done' or cmd == 'skip':
            waiting = False
        else:
            print("Type 'done' or 'skip'")
    except EOFError:
        waiting = False

if device_detected.is_set():
    print("\n=== Device detected! Waiting for interview...")
    time.sleep(5)
else:
    print("\n=== Checking for new device via bridge API ===")
    out, _, _ = sub_mqtt('zigbee2mqtt/bridge/event', count=1, timeout=10)
    print(f"Recent events: {out}")

    out, _, _ = sub_mqtt('zigbee2mqtt/bridge/devices', count=1, timeout=10)
    if out:
        topic_part, payload = out.split(' ', 1) if ' ' in out else ('', out)
        try:
            devices = json.loads(payload)
            new_devices = [d for d in devices if 'MCLH' in json.dumps(d) or 'LifeControl' in json.dumps(d)]
            if new_devices:
                print(f"Found MCLH-08: {json.dumps(new_devices, indent=2)}")
                device_detected.set()
            else:
                print(f"Total devices: {len(devices)}")
        except:
            pass

# Step 5: Disable Permit Join
print("\n=== Disabling Permit Join ===")
run_mqtt('zigbee2mqtt/bridge/request/permit_join', {"time": 0})
time.sleep(1)
out, _, _ = sub_mqtt('zigbee2mqtt/bridge/response/permit_join', count=1, timeout=5)
print(f"Response: {out or 'done'}")

log_thread_active = False
time.sleep(1)

if not device_detected.is_set():
    print("\n=== Device NOT detected. Restarting z2m... ===")
    out, _, _ = run("docker restart big-bear-zigbee2mqtt")
    print(f"Restart: {out}")
    print("Waiting 30s for z2m to restart...")
    time.sleep(30)
    
    print("\n=== Retry: Enabling Permit Join (254s) ===")
    run_mqtt('zigbee2mqtt/bridge/request/permit_join', {"time": 254})
    
    print("\n=== Reset MCLH-08 again (5-7sec hold → blink → release → short press) ===")
    print("Type 'done' when done:")
    try:
        input("> ")
    except EOFError:
        pass
    
    time.sleep(10)
    run_mqtt('zigbee2mqtt/bridge/request/permit_join', {"time": 0})
    
    out, _, _ = sub_mqtt('zigbee2mqtt/bridge/devices', count=1, timeout=10)
    print(f"Devices: {out[:500] if out else 'no response'}")
else:
    print("\n=== MCLH-08 successfully paired! ===")

ssh.close()
print("\nDone.")
