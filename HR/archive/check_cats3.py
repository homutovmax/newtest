import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

def run(cmd, timeout=10):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    return out

# Write and execute inline
channel = ssh.get_transport().open_session()
channel.exec_command('docker exec -i hr-web-1 python')
channel.send("import psycopg2\nconn = psycopg2.connect('postgresql://hr:hr@db/hr')\ncur = conn.cursor()\ncur.execute('SELECT category, count(*) FROM vacancies WHERE category IS NOT NULL GROUP BY category ORDER BY count(*) DESC')\nfor r in cur.fetchall(): print(r[0], r[1])\n".encode())
channel.shutdown_write()
import time
time.sleep(2)

out = b''
while True:
    try:
        chunk = channel.recv(4096)
        if not chunk: break
        out += chunk
    except: break
print(out.decode('utf-8', errors='replace'))
ssh.close()
