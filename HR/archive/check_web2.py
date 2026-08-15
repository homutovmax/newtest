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

ps = run('docker ps --format "{{.Names}} {{.Status}}"', 5)
print('Docker:', ps[0])

log = run('docker logs hr-web-1 --tail 15 2>&1', 5)
print('Logs:', log[0][:500])

health = run('curl -s http://localhost:8000/health 2>&1', 5)
print('Health:', health[0][:100])

ssh.close()
