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

# Read full api.py - look for URLs
print("=== api.py URLs ===")
api = run("cat /DATA/AppData/homeassistant/config/custom_components/haier_evo/api.py", 10)
# Extract URL patterns
import re
urls = set(re.findall(r'https?://[^\s"\'\)]+', api))
for u in sorted(urls):
    print(f"  {u}")

# Also check const.py
print("\n=== const.py ===")
const = run("cat /DATA/AppData/homeassistant/config/custom_components/haier_evo/const.py", 10)
print(const[:2000])

# Check if haieriot.com resolves from different DNS
print("\n=== haieriot.com DNS deep check ===")
for dns in ['1.1.1.1', '8.8.8.8', '77.88.8.8', '208.67.222.222']:
    out = run(f"nslookup -type=all haieriot.com {dns} 2>&1", 10)
    print(f"  {dns}:")
    for line in out.split('\n')[:10]:
        print(f"    {line}")

# Check if the actual API works from different network
print("\n=== Check haierevo API domain ===")
for domain in ['https://haieriot.com', 'https://api.haieriot.com', 'https://home.haieriot.com', 
               'https://app.haierevo.com', 'https://api.haierevo.com']:
    out = run(f"curl -s -o /dev/null -w '%{{http_code}}' --connect-timeout 10 {domain}/ 2>&1", 15)
    print(f"  {domain}: {out}")

# Check domain registration
print("\n=== Whois haieriot.com ===")
out = run("whois haieriot.com 2>/dev/null | head -30", 15)
if out and 'ERR' not in out:
    print(out[:1000])
else:
    # try alternative
    out = run("nslookup -type=soa haieriot.com 2>&1 | head -10", 15)
    print(out[:500])

# Check if there's config for alternative URLs
print("\n=== devices configs ===")
devices = run("ls /DATA/AppData/homeassistant/config/custom_components/haier_evo/devices/ 2>/dev/null", 10)
print(devices[:500] if devices else "(not found)")

ssh.close()
