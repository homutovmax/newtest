import paramiko, json

HOST = '192.168.1.92'
USER = 'root'
PASS = 'CHANGE_ME'
TOKEN = 'CHANGE_ME'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=10)

# Step 1: Clone yandex_smart_home from GitHub
print("=== Cloning yandex_smart_home ===")
stdin, stdout, stderr = ssh.exec_command(
    'cd /tmp && rm -rf ha-yandex_smart_home && '
    'git clone --depth 1 https://github.com/dmitry-k/ha-yandex_smart_home.git 2>&1',
    timeout=60)
out = stdout.read().decode('utf-8', errors='replace').strip()
err = stderr.read().decode('utf-8', errors='replace').strip()
print(f"  Clone: {out or err}")

# Step 2: Check what was downloaded
stdin, stdout, stderr = ssh.exec_command('ls -la /tmp/ha-yandex_smart_home/custom_components/ 2>&1', timeout=10)
out = stdout.read().decode('utf-8', errors='replace').strip()
print(f"  Contents: {out}")

# Step 3: Copy to HA custom_components
print("\\n=== Installing to HA ===")
stdin, stdout, stderr = ssh.exec_command(
    'cp -r /tmp/ha-yandex_smart_home/custom_components/yandex_smart_home '
    '/DATA/AppData/homeassistant/config/custom_components/ && '
    'ls -la /DATA/AppData/homeassistant/config/custom_components/yandex_smart_home/ 2>&1',
    timeout=15)
out = stdout.read().decode('utf-8', errors='replace').strip()
err = stderr.read().decode('utf-8', errors='replace').strip()
print(f"  Install: {out or err}")

# Step 4: Check manifest
stdin, stdout, stderr = ssh.exec_command(
    'cat /DATA/AppData/homeassistant/config/custom_components/yandex_smart_home/manifest.json 2>&1',
    timeout=10)
out = stdout.read().decode('utf-8', errors='replace').strip()
print(f"\\n=== Manifest ===")
try:
    manifest = json.loads(out)
    print(f"  Domain: {manifest.get('domain')}")
    print(f"  Name: {manifest.get('name')}")
    print(f"  Version: {manifest.get('version')}")
    print(f"  Requirements: {manifest.get('requirements')}")
except:
    print(f"  Raw: {out[:300]}")

# Step 5: Install requirements if any
stdin, stdout, stderr = ssh.exec_command(
    'cat /DATA/AppData/homeassistant/config/custom_components/yandex_smart_home/manifest.json 2>&1',
    timeout=10)
manifest = json.loads(stdout.read().decode('utf-8', errors='replace'))
requirements = manifest.get('requirements', [])
if requirements:
    print(f"\\n=== Installing requirements: {requirements} ===")
    for req in requirements:
        cmd = f'pip3 install "{req}" 2>&1'
        stdin, stdout, stderr = ssh.exec_command(cmd, timeout=120)
        out = stdout.read().decode('utf-8', errors='replace').strip()
        print(f"  {req}: {out[-200:]}")
else:
    print("\\n=== No requirements needed ===")

ssh.close()
