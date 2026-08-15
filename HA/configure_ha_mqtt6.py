import paramiko
import json
import time
from datetime import datetime, timezone

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)
sftp = ssh.open_sftp()

# 1. Stop HA
print("Stopping HA...")
ssh.exec_command('docker stop homeassistant')
time.sleep(5)

# 2. Read config entries
path = '/DATA/AppData/homeassistant/config/.storage/core.config_entries'
with sftp.open(path, 'r') as f:
    entries = json.loads(f.read().decode('utf-8'))

# Check if MQTT already exists
for entry in entries['data']['entries']:
    if entry['domain'] == 'mqtt':
        print("MQTT already configured!")
        sftp.close()
        ssh.close()
        exit()

# Generate entry ID
import uuid
entry_id = str(uuid.uuid4()).replace('-', '').upper()[:26]
# Make it look like a HA ULID
entry_id = '01' + entry_id[:24]

now_iso = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f') + '+00:00'

mqtt_entry = {
    "created_at": now_iso,
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
    "disabled_by": None,
    "discovery_keys": {},
    "domain": "mqtt",
    "entry_id": entry_id,
    "minor_version": 1,
    "modified_at": now_iso,
    "options": {},
    "pref_disable_new_entities": False,
    "pref_disable_polling": False,
    "source": "user",
    "subentries": [],
    "title": "MQTT",
    "unique_id": None,
    "version": 1
}

entries['data']['entries'].append(mqtt_entry)

with sftp.open(path, 'w') as f:
    f.write(json.dumps(entries, indent=2).encode('utf-8'))

print(f"MQTT entry added: {entry_id}")
print(f"Total entries: {len(entries['data']['entries'])}")

sftp.close()
ssh.close()
print("\nDone! Now starting HA...")
