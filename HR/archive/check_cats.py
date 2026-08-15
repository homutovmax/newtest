import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

def run(cmd, timeout=10):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    return out

out = run("docker exec hr-web-1 python -c \"
import psycopg2
conn = psycopg2.connect('postgresql://hr:hr@db/hr')
cur = conn.cursor()
cur.execute('SELECT category, count(*) FROM vacancies GROUP BY category ORDER BY count(*) DESC')
for r in cur.fetchall():
    print(r[0], '->', r[1])
\"", 10)
print(out)
ssh.close()
