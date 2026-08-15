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

# Step 1: Download from dext0r/yandex_smart_home dev branch
print("=== Downloading dext0r/yandex_smart_home (dev) ===")
out, err, code = run(
    'curl -sL -o /tmp/yash.zip '
    '"https://github.com/dext0r/yandex_smart_home/archive/refs/heads/dev.zip" '
    '&& ls -la /tmp/yash.zip',
    timeout=60)
print(f"  {out or err}")

if code != 0 or 'zip' not in out:
    print("  Download failed, trying alternative...")
    # Try the main branch
    out, err, code = run(
        'curl -sL -o /tmp/yash.zip '
        '"https://github.com/dext0r/yandex_smart_home/archive/refs/heads/main.zip" '
        '&& ls -la /tmp/yash.zip',
        timeout=60)
    print(f"  {out or err}")

# Step 2: Extract
print("\n=== Extracting ===")
out, err, code = run(
    'cd /tmp && rm -rf yash_extract && mkdir yash_extract && '
    'unzip -o yash.zip -d yash_extract 2>&1 | tail -5',
    timeout=30)
print(f"  {out or err}")

# Step 3: Find custom_components
out, err, code = run('find /tmp/yash_extract -name "yandex_smart_home" -type d 2>&1', timeout=10)
print(f"  Dir: {out}")

if out:
    # Step 4: Copy to HA
    print("\n=== Installing ===")
    src = out.split('\n')[0]
    out, err, code = run(
        f'cp -r {src} /DATA/AppData/homeassistant/config/custom_components/ '
        f'&& echo OK',
        timeout=15)
    print(f"  {out or err}")

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

            requirements = manifest.get('requirements', [])
            if requirements:
                print(f"\n=== Installing requirements ===")
                for req in requirements:
                    out2, err2, _ = run(f'pip3 install "{req}" 2>&1', timeout=120)
                    last_lines = (out2 or err2).split('\n')[-3:]
                    for l in last_lines:
                        if l.strip():
                            print(f"    {req}: {l.strip()}")
        except:
            print(f"  Raw: {out[:300]}")
else:
    print("  ERROR: Could not find yandex_smart_home directory in archive")

# Step 6: Verify installation
out, err, code = run('ls /DATA/AppData/homeassistant/config/custom_components/yandex_smart_home/ 2>&1', timeout=10)
print(f"\n=== Installed files ===")
print(f"  {out}")

ssh.close()
