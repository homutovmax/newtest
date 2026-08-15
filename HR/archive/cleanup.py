import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

def run(cmd, timeout=10):
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    code = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    return out

# Clean up deploy scripts
run('rm -f /opt/hr/check_*.py /opt/hr/deploy_*.py /opt/hr/fix_deploy*.py /opt/hr/setup_*.py /opt/hr/test_*.py /opt/hr/debug_*.py /opt/hr/retry_*.py /opt/hr/ts_*.py /opt/hr/fast_auth*.py /opt/hr/reauth*.py /opt/hr/quick_auth*.py /opt/hr/final_*.py /opt/hr/install_*.py /opt/hr/auth_*.py /opt/hr/get_auth*.py /opt/hr/config_*.py /opt/hr/update_sasl.py /opt/hr/run_pipeline.sh 2>/dev/null')

out = run('ls /opt/hr/*.py 2>/dev/null | wc -l')
print(f'Cleanup done. Remaining .py files: {out}')

ssh.close()
