import paramiko, json, urllib.request, zipfile, io, os

HOST = '192.168.1.92'
USER = 'root'
PASS = 'CHANGE_ME'
DEST = '/DATA/AppData/homeassistant/config/custom_components/yandex_station'

# 1. Download latest release
print("=== Downloading YandexStation latest release ===")
url = "https://github.com/AlexxIT/YandexStation/archive/refs/heads/master.zip"
print(f"  URL: {url}")
data = urllib.request.urlopen(url, timeout=30).read()
print(f"  Downloaded: {len(data)} bytes")

# 2. Extract custom_components/yandex_station
print("\n=== Extracting yandex_station ===")
zf = zipfile.ZipFile(io.BytesIO(data))
yandex_files = [f for f in zf.namelist() if f.startswith('YandexStation-master/custom_components/yandex_station/')]
print(f"  Found {len(yandex_files)} files")

# 3. Connect to server
print("\n=== Connecting to server ===")
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=10)
sftp = ssh.open_sftp()
print("  Connected")

# 4. Upload files
uploaded = 0
for f in yandex_files:
    if f.endswith('/'):
        # Create directory
        remote_dir = '/DATA/AppData/homeassistant/config/' + f.replace('YandexStation-master/', '')
        try:
            sftp.mkdir(remote_dir)
        except:
            pass
        continue
    
    remote_path = '/DATA/AppData/homeassistant/config/' + f.replace('YandexStation-master/', '')
    data_bytes = zf.read(f)
    
    # Create parent dirs
    parent = os.path.dirname(remote_path)
    try:
        sftp.mkdir(parent)
    except:
        pass
    
    with sftp.open(remote_path, 'wb') as rf:
        rf.write(data_bytes)
    uploaded += 1

print(f"  Uploaded {uploaded} files")

# 5. Verify manifest
manifest_path = '/DATA/AppData/homeassistant/config/custom_components/yandex_station/manifest.json'
with sftp.open(manifest_path, 'r') as f:
    manifest = json.load(f)
print(f"\n=== Manifest ===")
print(f"  Name: {manifest.get('name')}")
print(f"  Version: {manifest.get('version')}")
print(f"  Requirements: {manifest.get('requirements')}")
print(f"  Domain: {manifest.get('domain')}")

sftp.close()
ssh.close()
print("\n=== Done! YandexStation installed ===")
