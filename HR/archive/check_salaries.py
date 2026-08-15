import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

def run(cmd, timeout=10):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    return out

# Check salaries in DB
out = run("docker exec hr-web-1 python -c \"
import psycopg2
conn = psycopg2.connect('postgresql://hr:hr@db/hr')
cur = conn.cursor()
cur.execute('SELECT salary, count(*) FROM vacancies WHERE salary IS NOT NULL AND salary != \\'\\' GROUP BY salary ORDER BY count(*) DESC LIMIT 10')
rows = cur.fetchall()
for r in rows:
    print(repr(r[0]), '->', r[1])
print('---')
cur.execute('SELECT count(*) FROM vacancies')
print('Total:', cur.fetchone()[0])
cur.execute('SELECT count(*) FROM vacancies WHERE salary IS NOT NULL AND salary != \\'\\'')
print('With salary:', cur.fetchone()[0])
\""", 10)

print(out[:500])

ssh.close()
