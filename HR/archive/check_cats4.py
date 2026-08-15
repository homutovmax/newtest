import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

stdin, stdout, stderr = ssh.exec_command("docker exec hr-web-1 python -c 'import psycopg2; conn = psycopg2.connect(\"postgresql://hr:hr@db/hr\"); cur = conn.cursor(); cur.execute(\"SELECT category, count(*) FROM vacancies WHERE category IS NOT NULL GROUP BY category\"); print(cur.fetchall())'", timeout=10)
out = stdout.read().decode().strip()
err = stderr.read().decode().strip()
print('Out:', out)
if err: print('Err:', err)
ssh.close()
