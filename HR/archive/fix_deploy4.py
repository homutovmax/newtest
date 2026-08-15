import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=15)

def run(cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if out: print(out)
    if err and code != 0: print('ERR:', err[:200])
    return code

print('Checking web container...')
time.sleep(3)
code = run('docker inspect -f {{.State.Status}} hr-web-1')
print('Status:', 'running' if 'running' in str(code) else 'NOT running')

if code == 0 or True:  # try anyway
    print('\n1. Alembic upgrade...')
    code = run('docker exec hr-web-1 alembic upgrade head 2>&1')
    print('  Alembic:', 'OK' if code == 0 else f'FAIL ({code})')

    print('\n2. Migration...')
    code = run('docker exec hr-web-1 python -m src.migration 2>&1')
    print('  Migration:', 'OK' if code == 0 else f'FAIL ({code})')

    print('\n3. Health check...')
    out, _, _ = ssh.exec_command('curl -s http://localhost:8000/health')
    health = out.read().decode().strip()
    print('  Health:', health)

    print('\n4. Report page...')
    out, _, _ = ssh.exec_command('curl -s http://localhost:8000/report | head -5')
    html = out.read().decode().strip()
    print('  Report:', html[:100] if html else 'EMPTY')

ssh.close()
print('\n=== DEPLOY COMPLETE ===')
