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
sftp.close()
print('Uploaded')

run("docker exec hr-web-1 python -c \"import psycopg2; conn = psycopg2.connect('postgresql://hr:hr@db/hr'); cur = conn.cursor(); cur.execute('UPDATE vacancies SET category = NULL'); conn.commit()\"", 10)

out, _ = run('docker exec hr-web-1 python -m src.migration 2>&1', 15)
print('Migration:', out[:500])

# Verify categories
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(10)
s.connect(('100.112.4.123', 8000))
s.send(b'GET /report?tab=other HTTP/1.0\r\nHost: health\r\n\r\n')
resp = s.recv(4096).decode('utf-8', errors='replace')
s.close()
size_other = len(resp)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(10)
s.connect(('100.112.4.123', 8000))
s.send(b'GET /report?tab=telecom HTTP/1.0\r\nHost: health\r\n\r\n')
resp = s.recv(4096).decode('utf-8', errors='replace')
s.close()
size_telecom = len(resp)

print(f'other={size_other}b, telecom={size_telecom}b')
print('Fix effective!' if size_other != size_telecom else 'STILL BROKEN')

ssh.close()
