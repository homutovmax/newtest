import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

def run(cmd, timeout=10):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    return out

time.sleep(5)

print('Health:', run('curl -s http://localhost:8000/health', 5))

# Check double new
out = run("curl -s http://localhost:8000/report 2>&1", 10)
new_count = out.count('status-new')
print('status-new count:', new_count, '(was 2 per vacancy)')

# Check cover bold
out = run("curl -s http://localhost:8000/cover/hh-133207087 2>&1", 10)
bold_count = out.count('<strong>')
br_count = out.count('<br>')
print('Cover: <strong>=', bold_count, ' <br>=', br_count)

# Check resume label
out = run('curl -s "http://localhost:8000/resume?title=CTO+AI&company=Test&scenario=2"', 10)
import re
m = re.search(r'Сценарий:</strong> ([^<]+)', out)
if m:
    print('Resume label:', m.group(1))
else:
    # try finding scenario text
    for line in out.split('\n'):
        if 'ценарий' in line:
            print('Scenario line:', line.strip()[:100])

ssh.close()
