import paramiko, json

HOST = '192.168.1.92'
USER = 'root'
PASS = 'CHANGE_ME'
TOKEN = 'CHANGE_ME'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=10)

def run(cmd, timeout=60):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    exit_code = stdout.channel.recv_exit_status()
    out = stdout.read().decode('utf-8', errors='replace').strip()
    err = stderr.read().decode('utf-8', errors='replace').strip()
    return out, err, exit_code

# Step 1: Download from GitHub API (zip archive of master)
print("=== Downloading yandex_smart_home ===")
out, err, code = run(
    'curl -sL -o /tmp/yash.zip '
    '"https://github.com/dmitry-k/ha-yandex_smart_home/archive/refs/heads/master.zip" '
    '&& ls -la /tmp/yash.zip',
    timeout=60)
print(f"  Download: {out or err}")

# Step 2: Unzip
print("\n=== Extracting ===")
out, err, code = run(
    'cd /tmp && rm -rf yash_extract && mkdir yash_extract && '
    'unzip -o yash.zip -d yash_extract 2>&1 | tail -5',
    timeout=30)
print(f"  Extract: {out or err}")

# Step 3: Find the custom_components directory
out, err, code = run('find /tmp/yash_extract -name "yandex_smart_home" -type d 2>&1', timeout=10)
print(f"  Found: {out}")

# Step 4: Copy to HA
print("\n=== Installing ===")
out, err, code = run(
    'cp -r /tmp/yash_extract/ha-yandex_smart_home-master/custom_components/yandex_smart_home '
    '/DATA/AppData/homeassistant/config/custom_components/ '
    '&& echo "OK" || echo "FAILED"',
    timeout=15)
print(f"  Copy: {out or err}")

# Step 5: Check manifest
out, err, code = run(
    'cat /DATA/AppData/homeassistant/config/custom_components/yandex_smart_home/manifest.json',
    timeout=10)
if out:
    try:
        manifest = json.loads(out)
        print(f"\n=== Manifest ===")
        print(f"  Domain: {manifest.get('domain')}")
        print(f"  Name: {manifest.get('name')}")
        print(f"  Version: {manifest.get('version')}")
        print(f"  Requirements: {manifest.get('requirements', [])}")
        
        # Install requirements
        requirements = manifest.get('requirements', [])
        if requirements:
            print(f"\n=== Installing requirements ===")
            for req in requirements:
                out2, err2, _ = run(f'pip3 install "{req}" 2>&1', timeout=120)
                last_line = (out2 or err2).split('\n')[-1] if (out2 or err2) else 'no output'
                print(f"  {req}: {last_line}")
    except:
        print(f"  Manifest: {out[:300]}")
else:
    print(f"  Error: {err}")

# Step 6: List all custom_components
out, err, code = run('ls /DATA/AppData/homeassistant/config/custom_components/', timeout=10)
print(f"\n=== Custom Components ===")
print(f"  {out}")

ssh.close()
