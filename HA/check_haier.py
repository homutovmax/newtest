import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=15)

def run(cmd, timeout=15):
    try:
        stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
        return stdout.read().decode('utf-8', errors='replace').strip()
    except Exception as e:
        return f'ERR: {e}'

# Read haier_evo config_flow.py - check options/setup modes
print("=== config_flow.py ===")
flow = run("cat /DATA/AppData/homeassistant/config/custom_components/haier_evo/config_flow.py 2>/dev/null | head -200", 10)
print(flow[:3000] if flow else "(not found)")

# Read haier_evo api.py to see if local mode exists
print("\n=== api.py (search for local) ===")
api_loc = run("grep -n -i 'local\|lan\|ip_address\|host\|port' /DATA/AppData/homeassistant/config/custom_components/haier_evo/api.py 2>/dev/null | head -30", 10)
print(api_loc[:2000] if api_loc else "(not found)")

# Read manifest.json
print("\n=== manifest.json ===")
manifest = run("cat /DATA/AppData/homeassistant/config/custom_components/haier_evo/manifest.json 2>/dev/null", 10)
print(manifest if manifest else "(not found)")

# Read full api.py
print("\n=== api.py (full) ===")
api = run("cat /DATA/AppData/homeassistant/config/custom_components/haier_evo/api.py 2>/dev/null", 10)
print(api[:5000] if api else "(not found)")

# Read config.py
print("\n=== config.py ===")
config = run("cat /DATA/AppData/homeassistant/config/custom_components/haier_evo/config.py 2>/dev/null", 10)
print(config[:3000] if config else "(not found)")

# Read select.py - contains mode selection
print("\n=== select.py ===")
select = run("cat /DATA/AppData/homeassistant/config/custom_components/haier_evo/select.py 2>/dev/null", 10)
print(select[:2000] if select else "(not found)")

# Check the __init__.py
print("\n=== __init__.py ===")
init = run("cat /DATA/AppData/homeassistant/config/custom_components/haier_evo/__init__.py 2>/dev/null", 10)
print(init[:3000] if init else "(not found)")

# Check if there's a GitHub repo for haier_evo documentation
print("\n=== All haier_evo files ===")
files = run("find /DATA/AppData/homeassistant/config/custom_components/haier_evo -type f -name '*.py' -o -name '*.json' -o -name '*.md' 2>/dev/null", 10)
print(files if files else "(not found)")

# Check the config entry options for haier_evo
TOKEN = "CHANGE_ME"
print("\n=== haier_evo config entry options ===")
opts = run("curl -s -H 'Authorization: Bearer " + TOKEN + "' http://localhost:8123/api/config/config_entries/entry/01KNHRHZDTS874HSM6M4WWQYP5 2>&1 | python3 -c \"import sys,json; d=json.load(sys.stdin); print(json.dumps(d, indent=2, ensure_ascii=False))\" 2>/dev/null", 10)
print(opts[:2000] if opts else "(not found)")

ssh.close()
