import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

def run(cmd, timeout=15):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()[:300]
    return out, err, code

# Write test script to mounted volume
channel = ssh.get_transport().open_session()
channel.exec_command('cat > /opt/hr/test_email.py')
channel.send("""import sys
sys.path.insert(0, '/app')
from src.notifications.email import send_digest
send_digest("HR SMTP Test", "<h2>Test from Container</h2><p>SMTP via smtplib works!</p>")
""".encode())
channel.shutdown_write()
code = channel.recv_exit_status()
print('Write:', code)

# Run from container
out, _, _ = run('docker exec hr-web-1 python /app/test_email.py 2>&1', 15)
print('Test:', out)

# Cleanup
out, _, _ = run('rm /opt/hr/test_email.py')
ssh.close()
