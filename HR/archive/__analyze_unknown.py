import socket, re

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(10)
s.connect(('100.112.4.123', 8000))
s.send(b'GET /report?tab=other HTTP/1.0\r\nHost: test\r\n\r\n')
resp = b''
while True:
    c = s.recv(16384)
    if not c: break
    resp += c
s.close()
html = resp.decode('utf-8', errors='replace')
body = html.split('\r\n\r\n', 1)[1]

# Extract all titles from unknown vacancies
titles = re.findall(r'<h3>(.+?)</h3>', body)
print(f'Unknown vacancies: {len(titles)}')
print('\n=== First 60 titles ===')
for t in titles[:60]:
    print(f'  {t}')

print(f'\n=== Last 20 titles ===')
for t in titles[-20:]:
    print(f'  {t}')
