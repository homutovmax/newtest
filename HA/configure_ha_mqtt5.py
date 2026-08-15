import paramiko
import json
import time
import uuid
import sys

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)
sftp = ssh.open_sftp()

# 1. Stop HA
print("Stopping HA...")
ssh.exec_command('docker stop homeassistant')
time.sleep(5)

# 2. Read and modify config_entries to add MQTT
path = '/DATA/AppData/homeassistant/config/.storage/core.config_entries'
with sftp.open(path, 'r') as f:
    entries = json.loads(f.read().decode('utf-8'))

print(f"Current entries: {len(entries.get('data', {}).get('entries', {}))}")

# Check if MQTT already exists
for eid, entry in entries['data']['entries'].items():
    domain = entry.get('domain')
    if domain == 'mqtt':
        print("MQTT already configured!")
        ssh.close()
        sys.exit(0)

# Create MQTT entry
entry_id = str(uuid.uuid4()).replace('-', '')
now = time.time()
mqtt_entry = {
    "version": 1,
    "minor_version": 1,
    "domain": "mqtt",
    "title": "",
    "data": {
        "broker": "127.0.0.1",
        "port": 1883,
        "username": "mqtt",
        "password": "CHANGE_ME",
        "discovery": True,
        "discovery_prefix": "homeassistant",
        "birth_message": {
            "topic": "homeassistant/status",
            "payload": "online"
        },
        "will_message": {
            "topic": "homeassistant/status",
            "payload": "offline"
        }
    },
    "options": {},
    "pref_domain_enabled": {},
    "source": "user",
    "unique_id": "",
    "disabled_by": None
}

# HA 2026.5 format - entries is a dict with key being entry_id
entries['data']['entries'][entry_id] = mqtt_entry

# Update version
entries['version'] = entries.get('version', 1)
entries['data']['version'] = entries['data'].get('version', 1)

with sftp.open(path, 'w') as f:
    f.write(json.dumps(entries, indent=2).encode('utf-8'))

print("MQTT entry added successfully")
print(f"Entry ID: {entry_id}")
print(f"Now {len(entries['data']['entries'])} entries")

sftp.close()
ssh.close()

print("Start HA with: docker start homeassistant")
print("Or it will auto-restart if restart policy is 'unless-stopped'")
