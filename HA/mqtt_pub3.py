import paramiko, json, sys, uuid, base64, os

HOST = '192.168.1.92'
USER = 'root'
PASS = 'CHANGE_ME'

topic = sys.argv[1]
payload_b64 = sys.argv[2]
payload = json.loads(base64.b64decode(payload_b64).decode())
timeout = int(sys.argv[3]) if len(sys.argv) > 3 else 15

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=10)

tmpfile = f'/tmp/mqtt_payload_{uuid.uuid4().hex[:8]}.json'
with ssh.open_sftp() as sftp:
    with sftp.open(tmpfile, 'w') as f:
        f.write(json.dumps(payload))

cmd = f'mosquitto_pub -h localhost -p 1883 -u mqtt -P CHANGE_ME -t "{topic}" -f {tmpfile} && rm {tmpfile}'
stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
exit_code = stdout.channel.recv_exit_status()
out = stdout.read().decode('utf-8', errors='replace').strip()
err = stderr.read().decode('utf-8', errors='replace').strip()
if out:
    print(out)
if err:
    print(f"[STDERR] {err}")
sys.exit(exit_code)
