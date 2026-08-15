import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

def run(cmd, timeout=10):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    return out

# 1. Kill stale processes
run("pkill -f 'tailscale up' 2>/dev/null")
run("pkill -f 'tailscale' 2>/dev/null")
run("pkill -f 'tailscale' 2>/dev/null")

# 2. Install screen
run("apt-get install -y -qq screen 2>/dev/null")

# 3. Full reset
run("systemctl stop tailscaled; rm -rf /var/lib/tailscale; systemctl start tailscaled")
time.sleep(5)

# 4. Run in screen
run('screen -dmS ts tailscale up --accept-dns=false')
time.sleep(8)

# 5. Capture output  
out = run("cat /tmp/ts_out.txt 2>/dev/null")
if not out:
    # Try screen's hardcopy
    run("screen -S ts -X hardcopy /tmp/ts_out.txt 2>/dev/null")
    time.sleep(1)
    out = run("cat /tmp/ts_out.txt 2>/dev/null")

print('Output:', out[:500])

# 6. Also check journal for URL
out2 = run("journalctl -u tailscaled --no-pager -n 10 2>&1 | grep -o 'https://[^ ]*'")
print('URL from journal:', out2[:200])

# 7. Check if screen is running
out3 = run('screen -ls 2>&1')
print('Screen:', out3[:200])

import re
all_text = out + ' ' + out2
urls = re.findall(r'https://[^\s]+', all_text)
for u in urls:
    if 'login.tailscale.com' in u:
        print(f'\n=== ОТКРОЙТЕ В БРАУЗЕРЕ ===')
        print(u)

ssh.close()
