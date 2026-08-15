import paramiko, time, socket

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=15)

# Check logs
stdin, stdout, stderr = ssh.exec_command('docker logs hr-web-1 --tail 20 2>&1')
print('LOGS:', stdout.read().decode()[:1000])
stdin, stdout, stderr = ssh.exec_command('docker ps --format "{{.Names}} {{.Status}}"')
print('PS:', stdout.read().decode().strip())

# Try curl after a moment
import time
time.sleep(3)
stdin, stdout, stderr = ssh.exec_command('curl -s http://localhost:8000/health')
print('Health:', stdout.read().decode()[:200])

ssh.close()
