import paramiko, json, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

transport = ssh.get_transport()
channel = transport.open_session()
channel.exec_command('docker exec -i hr-web-1 python')
time.sleep(1)

code = """import json
with open("vacancies_history.json", "r") as f:
    data = json.load(f)
# Sample 5 entries
count = 0
cats = set()
for k, v in data.items():
    cat = v.get("category")
    cats.add(str(cat))
    if count < 5:
        print(f"  {k}: cat={cat!r} title={v.get('title','')[:40]}")
    count += 1
print(f"Total: {count} entries, unique categories: {cats}")
"""
channel.send(code.encode())
channel.shutdown_write()

import time
time.sleep(3)
out = b''
try:
    while True:
        chunk = channel.recv(4096)
        if not chunk: break
        out += chunk
except: pass
print(out.decode('utf-8', errors='replace'))
ssh.close()
