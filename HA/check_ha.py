import paramiko, json, sys

HOST = '192.168.1.92'
USER = 'root'
PASS = 'CHANGE_ME'
TOKEN = 'CHANGE_ME'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=10)

cmd = f'curl -s -H "Authorization: Bearer {TOKEN}" -H "Content-Type: application/json" "http://localhost:8123/api/states" | python3 -c "import sys,json; data=json.load(sys.stdin); mclh=[s for s in data if chr(0x30)*2+chr(0x30)+chr(0x31)+chr(0x35)+chr(0x38)+chr(0x30)+chr(0x30)+chr(0x30)+chr(0x64)+chr(0x39)+chr(0x63)+chr(0x64)+chr(0x32)+chr(0x63) in s[chr(0x65)+chr(0x6e)+chr(0x74)+chr(0x69)+chr(0x74)+chr(0x79)+chr(0x5f)+chr(0x69)+chr(0x64)]]; [print(s[chr(0x65)+chr(0x6e)+chr(0x74)+chr(0x69)+chr(0x74)+chr(0x79)+chr(0x5f)+chr(0x69)+chr(0x64)], chr(61)*3, s[chr(0x73)+chr(0x74)+chr(0x61)+chr(0x74)+chr(0x65)]) for s in mclh]"'

stdin, stdout, stderr = ssh.exec_command(cmd, timeout=20)
exit_code = stdout.channel.recv_exit_status()
out = stdout.read().decode('utf-8', errors='replace').strip()
err = stderr.read().decode('utf-8', errors='replace').strip()
print(out if out else err if err else 'no output')
sys.exit(exit_code)
