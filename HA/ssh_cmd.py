import paramiko, sys, json

HOST = '192.168.1.92'
USER = 'root'
PASS = 'CHANGE_ME'

timeout = int(sys.argv[1]) if len(sys.argv) > 1 else 15
cmd = ' '.join(sys.argv[2:]) if len(sys.argv) > 2 else 'echo no command'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=10)

stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
exit_code = stdout.channel.recv_exit_status()
out = stdout.read().decode('utf-8', errors='replace').strip()
err = stderr.read().decode('utf-8', errors='replace').strip()

if out:
    print(out)
if err:
    print(f"[STDERR] {err}", file=sys.stderr)
sys.exit(exit_code)
