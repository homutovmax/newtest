import paramiko, json

HOST = '192.168.1.92'
USER = 'root'
PASS = 'CHANGE_ME'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=10)

script = '''
import urllib.request, json

# Search GitHub for yandex smart home repos
url = "https://api.github.com/search/repositories?q=yandex+smart+home+home-assistant&sort=stars&per_page=10"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
try:
    data = json.load(urllib.request.urlopen(req, timeout=15))
    for r in data.get("items", []):
        print(f"{r['full_name']} | stars={r['stargazers_count']} | branch={r['default_branch']} | {r.get('description','')[:80]}")
except Exception as e:
    print(f"Error: {e}")

# Also try specific known repos
print("\\n=== Trying known repos ===")
repos = [
    "https://github.com/dmitry-k/ha-yandex_smart_home",
    "https://github.com/alryaz/ha-yandex_smart_home",
    "https://github.com/AvenTok/ha-yandex_smart_home",
    "https://github.com/lepnik/ha-yandex_smart_home",
    "https://github.com/gl0bal01/ha-yandex_smart_home",
    "https://github.com/AKOnline/ha-yandex_smart_home",
    "https://github.com/sergeymaysak/ha-yandex_smart_home",
]
for repo_url in repos:
    try:
        req = urllib.request.Request(repo_url, headers={"User-Agent": "Mozilla/5.0"})
        urllib.request.urlopen(req, timeout=5)
        print(f"  FOUND: {repo_url}")
    except urllib.error.HTTPError as e:
        print(f"  {repo_url}: {e.code}")
    except Exception as e:
        print(f"  {repo_url}: {e}")
'''

with ssh.open_sftp() as sftp:
    with sftp.open('/tmp/find_yandex.py', 'w') as f:
        f.write(script)

cmd = 'python3 /tmp/find_yandex.py'
stdin, stdout, stderr = ssh.exec_command(cmd, timeout=60)
exit_code = stdout.channel.recv_exit_status()
out = stdout.read().decode('utf-8', errors='replace').strip()
err = stderr.read().decode('utf-8', errors='replace').strip()
for line in (out + '\n' + err).split('\n'):
    if line.strip():
        print(line.strip())
ssh.close()
