import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

def run(cmd, timeout=10):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()[:300]
    return out, err, code

# Flush queue and resend test
out, _, _ = run('postqueue -f', 5)
print('Flush:', out[:200])

import time
time.sleep(5)

out, _, _ = run('tail -20 /var/log/mail.log 2>&1')
print('Mail log:')
print(out)

out, _, _ = run('mailq 2>&1')
print('Queue:', out[:300])

ssh.close()
