import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(10)
s.connect(('100.112.4.123', 8000))
s.send(b'GET /analytics HTTP/1.0\r\nHost: test\r\n\r\n')
resp = b''
while True:
    c = s.recv(4096)
    if not c: break
    resp += c
s.close()
html = resp.decode('utf-8', errors='replace')
body = html.split('\r\n\r\n', 1)[1]
print('Length:', len(body))
print('Status:', html.split('\r\n')[0])
# Show key parts
import re
for line in body.split('\n'):
    if 'bar' in line and 'label' not in line and len(line) > 30:
        print(line.strip()[:100])
    elif 'fill' in line and '%' in line:
        print(line.strip()[:100])
