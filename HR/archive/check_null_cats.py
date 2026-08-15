import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

transport = ssh.get_transport()
channel = transport.open_session()
channel.exec_command('docker exec -i hr-web-1 python')
time.sleep(1)

# Send Python code line by line
code = """import psycopg2
conn = psycopg2.connect("postgresql://hr:hr@db/hr")
cur = conn.cursor()
cur.execute("SELECT DISTINCT category FROM vacancies LIMIT 10")
rows = cur.fetchall()
print("Categories:", rows)
cur.execute("SELECT count(*) FROM vacancies WHERE category IS NULL")
null_count = cur.fetchone()[0]
cur.execute("SELECT count(*) FROM vacancies")
total = cur.fetchone()[0]
print(f"NULL category: {null_count}/{total}")
# Check first vacancy data
cur.execute("SELECT id, category, source FROM vacancies LIMIT 3")
for r in cur.fetchall():
    print(f"  id={r[0]} cat={r[1]} src={r[2]}")
"""
channel.send(code.encode())
channel.shutdown_write()

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
