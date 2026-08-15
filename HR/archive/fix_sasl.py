import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

def run(cmd, timeout=30):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()[:500]
    return out, err, code

# 1. Install SASL modules for PLAIN auth
print('Installing SASL modules...')
out, err, code = run('DEBIAN_FRONTEND=noninteractive apt-get install -y libsasl2-modules 2>&1 | tail -3', 30)
print('Install:', code, out[-200:])

# 2. Force IPv4 for postfix
out, _, _ = run('postconf -e "smtp_address_preference = ipv4"')
print('IPv4:', out)

# 3. Verify SASL mechanisms available
out, _, _ = run('postconf smtp_sasl_security_options')
print('SASL opts:', out)

# 4. Restart
out, _, _ = run('systemctl restart postfix')
print('Restart:', out)

# 5. Flush queue to retry
out, _, _ = run('postqueue -f')
print('Flush:', out)

# 6. Wait and check
import time
time.sleep(5)

out, _, _ = run('tail -15 /var/log/mail.log 2>&1')
print('Mail log:')
print(out)

out, _, _ = run('mailq 2>&1')
print('Queue:', out[:300])

ssh.close()
