import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=15)

def run(cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode('utf-8').strip()
    err = stderr.read().decode('utf-8').strip()
    code = stdout.channel.recv_exit_status()
    return out, err, code

print('=== Containers ===')
out, err, _ = run("docker ps -a --filter name=hr --format '{{.Names}} {{.Status}}'")
print(out or '(empty)')
if err: print('ERR:', err)

print('\n=== Web logs (last 30) ===')
out, err, _ = run('docker logs hr-web-1 2>&1 | tail -30')
print(out or '(empty)')
if err: print('ERR:', err)

print('\n=== DB logs (last 10) ===')
out, err, _ = run('docker logs hr-db-1 2>&1 | tail -10')
print(out or '(empty)')
if err: print('ERR:', err)

print('\n=== Try running migrate directly ===')
# Create a temporary container to run migration
out, err, code = run('docker run --rm --network hr_default -e DB_URL=postgresql://hr:hr@db/hr hr-web python -m src.migration 2>&1')
print(out or '(empty)')
if err: print('ERR:', err)
print('Exit:', code)

ssh.close()
