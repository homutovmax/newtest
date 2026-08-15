import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

def run(cmd, timeout=15):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()[:500]
    return out, err, code

# Configure Postfix for Yandex SMTP relay
cmd = '''
postconf -e "relayhost = smtp.yandex.ru:587"
postconf -e "smtp_use_tls = yes"
postconf -e "smtp_sasl_auth_enable = yes"
postconf -e "smtp_sasl_security_options = noanonymous"
postconf -e "smtp_sasl_password_maps = hash:/etc/postfix/sasl_passwd"
'''
out, err, code = run(cmd)
print('Postfix config:', code)

# Write SASL password file
pw = 'smtp.yandex.ru:587 maximumkh@yandex.ru:fdoedrbwltfqsujt'
transport = ssh.get_transport()
channel = transport.open_session()
channel.exec_command('cat > /etc/postfix/sasl_passwd')
channel.send(pw.encode())
channel.shutdown_write()
code = channel.recv_exit_status()
print('SASL password:', code)

# Hash the password file
out, _, _ = run('chmod 600 /etc/postfix/sasl_passwd && postmap /etc/postfix/sasl_passwd')
print('Hash:', out)

# Restart postfix
out, _, _ = run('systemctl restart postfix')
print('Restart:', out)

# Test send
out, _, _ = run('echo "Subject: HR Test\n\nTest from HR server via Yandex relay" | sendmail -v -f maximumkh@yandex.ru homutov.m@gmail.com 2>&1 | tail -10')
print('Test:', out[:500])

# Check mail log
out, _, _ = run('tail -20 /var/log/mail.log 2>&1')
print('\nMail log:')
print(out)

ssh.close()
