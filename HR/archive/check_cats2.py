import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

transport = ssh.get_transport()
channel = transport.open_session()
channel.exec_command('docker exec hr-web-1 python')

script = '''
import psycopg2
conn = psycopg2.connect("postgresql://hr:hr@db/hr")
cur = conn.cursor()
cur.execute("SELECT category, count(*) FROM vacancies GROUP BY category ORDER BY count(*) DESC")
for r in cur.fetchall():
    print(repr(r[0]), "->", r[1])
'''
channel.send(script.encode())
channel.shutdown_write()
import time
time.sleep(2)
out = channel.recv(4096).decode()
print(out)
ssh.close()
