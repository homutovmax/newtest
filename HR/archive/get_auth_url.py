import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

# Run tailscale up with pipe to capture URL before it blocks
stdin, stdout, stderr = ssh.exec_command('tailscale up 2>&1; echo "EXIT:$?"', timeout=8)

# Wait briefly for output
time.sleep(2)

# Try to read what's available (non-blocking)
import select
out_data = b''
err_data = b''
while True:
    # Just read what's there
    try:
        chunk = stdout.read(4096)
        if not chunk:
            break
        out_data += chunk
    except:
        break

try:
    chunk = stderr.read(4096)
    if chunk:
        err_data += chunk
except:
    pass

result = out_data.decode('utf-8', errors='replace')
print(result[:1000])
if err_data:
    print('STDERR:', err_data.decode()[:500])

# If we got the URL, user needs to visit it
if 'https://' in result:
    import re
    urls = re.findall(r'https://[^\s]+', result)
    for u in urls:
        print('\n=== VISIT THIS URL TO AUTHENTICATE ===')
        print(u)

ssh.close()
