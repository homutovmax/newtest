import socket

def fetch(url):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(10)
    s.connect(('100.112.4.123', 8000))
    s.send(f'GET {url} HTTP/1.0\r\nHost: test\r\n\r\n'.encode())
    resp = b''
    while True:
        chunk = s.recv(4096)
        if not chunk: break
        resp += chunk
    s.close()
    # Split headers and body
    parts = resp.decode('utf-8', errors='replace').split('\r\n\r\n', 1)
    return parts[1] if len(parts) > 1 else ''

# Check different tabs
for tab in ['all', 'telecom', 'other']:
    html = fetch(f'/report?tab={tab}')
    # Count vacancy divs
    vcount = html.count('<div class="vacancy">')
    print(f'tab={tab}: {len(html)}b, {vcount} vacancies')
    if vcount < 5:
        print(f'  Content: {html[:300]}...')
