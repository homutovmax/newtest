import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

def run(cmd, timeout=15):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    return out, code

sftp = ssh.open_sftp()
sftp.put(r'C:\NEWTEST\HR\src\migration.py', '/opt/hr/src/migration.py', confirm=False)
print('Uploaded migration.py')
sftp.close()

# Clear categories, re-import
out, _ = run("docker exec hr-web-1 python -c \"import psycopg2; conn = psycopg2.connect('postgresql://hr:hr@db/hr'); cur = conn.cursor(); cur.execute('UPDATE vacancies SET category = NULL'); conn.commit(); print('Categories cleared')\"", 10)
print('Clear:', out)

out, _ = run('docker exec hr-web-1 python -m src.migration 2>&1', 15)
print('Migration:', out[:500])

# Verify
out, _ = run("docker exec hr-web-1 python -c \"import psycopg2; conn = psycopg2.connect('postgresql://hr:hr@db/hr'); cur = conn.cursor(); cur.execute('SELECT category, count(*) FROM vacancies WHERE category IS NOT NULL GROUP BY category ORDER BY count(*) DESC'); print(cur.fetchall())\"", 10)
print('Categories after fix:', out)

ssh.close()
