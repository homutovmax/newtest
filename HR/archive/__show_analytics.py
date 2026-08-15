import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(10)
s.connect(('100.112.4.123', 8000))
s.send(b'GET /analytics HTTP/1.0\r\nHost: test\r\n\r\n')
resp = b''
while True:
    c = s.recv(16384)
    if not c: break
    resp += c
s.close()
html = resp.decode('utf-8', errors='replace')
body = html.split('\r\n\r\n', 1)[1]

# Show all text content (strip tags)
import re
text = re.sub(r'<[^>]+>', '\n', body)
text = re.sub(r'\n+', '\n', text).strip()
print(text[:2000])
