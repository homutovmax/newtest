import paramiko, urllib.request, json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

# Get a valid vacancy ID from DB
stdin, stdout, stderr = ssh.exec_command("""docker exec hr-web-1 python -c "
from src.database import SessionLocal
from src.models import Vacancy
s = SessionLocal()
v = s.query(Vacancy).filter(Vacancy.cover_text.isnot(None)).first()
if v:
    print(f'ID={v.id}')
else:
    print('NO_COVER')
s.close()
" 2>&1""")
out = stdout.read().decode('utf-8', errors='replace')
print('DB query:', out.strip())

# Extract ID
vid = ''
for line in out.split('\n'):
    if line.startswith('ID='):
        vid = line.split('ID=')[1].strip()

if vid:
    r = urllib.request.urlopen(f'http://192.168.1.92:8000/cover/{vid}', timeout=10)
    body = r.read().decode('utf-8')
    print(f'/cover/{vid} -> Status: {r.status}')
    print(f'Has cover-container: {"cover-container" in body}')
    print(f'Has <main>: {"<main>" in body}')
    print(f'Has CSP: {"Content-Security-Policy" in body}')
else:
    print('No vacancy with cover_text found')

ssh.close()
