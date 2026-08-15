import paramiko, time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

def run(cmd, timeout=15):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()[:500]
    return out, err, code

# Update SASL password
transport = ssh.get_transport()
channel = transport.open_session()
channel.exec_command('cat > /etc/postfix/sasl_passwd')
channel.send(b'smtp.yandex.ru:587 maximumkh@yandex.ru:CHANGE_ME')
channel.shutdown_write()
code = channel.recv_exit_status()
print('Write SASL:', code)

# Hash
out, _, _ = run('postmap /etc/postfix/sasl_passwd && chmod 600 /etc/postfix/sasl_passwd /etc/postfix/sasl_passwd.db')
print('Hash:', out)

# Restart
out, _, _ = run('systemctl restart postfix')
print('Restart:', out)

# Flush old queue
out, _, _ = run('postsuper -d ALL 2>/dev/null; mailq')
print('Queue cleared:', out[:200])

# Send fresh test
out, _, _ = run('echo "Subject: HR Test 2\n\nTest from HR server via Yandex relay" | sendmail -v -f maximumkh@yandex.ru homutov.m@gmail.com 2>&1 | tail -5')
print('Send:', out[:300])

time.sleep(5)

out, _, _ = run('tail -20 /var/log/mail.log 2>&1')
print('\nMail log:')
print(out)

out, _, _ = run('mailq 2>&1')
print('Queue:', out[:200])

ssh.close()
