import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

def run(cmd, timeout=10):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    return out

sftp = ssh.open_sftp()
sftp.put(r'C:\NEWTEST\HR\web\app.py', '/opt/hr/web/app.py', confirm=False)
sftp.put(r'C:\NEWTEST\HR\web\templates\report.html', '/opt/hr/web/templates/report.html', confirm=False)
sftp.put(r'C:\NEWTEST\HR\web\templates\cover.html', '/opt/hr/web/templates/cover.html', confirm=False)
sftp.close()
print('Files uploaded')

# Restart web (no rebuild needed - files are mounted via /opt/hr:/app)
run('docker restart hr-web-1')
time.sleep(5)

# Test
out = run('curl -s http://localhost:8000/health')
print('Health:', out)

# Check no double "new" tags
out = run("curl -s http://localhost:8000/report 2>&1 | grep -o 'status-new' | wc -l")
print('Double new check:', int(out.strip()), '- should be fewer than before')

# Check cover rendering
out = run("curl -s http://localhost:8000/cover/hh-133207087 2>&1 | grep -o '<strong>' | wc -l")
print('Cover bold tags:', out)

# Check resume label
out = run('curl -s "http://localhost:8000/resume?title=CTO+AI&company=Test&scenario=2" 2>&1 | grep -oP "Сценарий.*?<"')
print('Resume label:', out[:200])

ssh.close()
