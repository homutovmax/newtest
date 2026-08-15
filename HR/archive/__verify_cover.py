import urllib.request, re

r = urllib.request.urlopen('http://100.112.4.123:8000/cover/hh-133207087', timeout=10)
html = r.read().decode('utf-8', errors='replace')

start = html.find('<div class="cover-container">')
end = html.find('</div>', start)
if start >= 0:
    cover = html[start+len('<div class="cover-container">'):end]
    preview = re.sub(r'<[^>]+>', ' ', cover)
    preview = re.sub(r'\s+', ' ', preview).strip()
    print('Cover text:')
    print(preview[:600])
else:
    print('Cover container not found')

# Also check funnel URL
import ssl
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
try:
    r = urllib.request.urlopen('https://ibox-z3-2.taila7bc1e.ts.net/health', context=ctx, timeout=10)
    print(f'\nFunnel health: {r.status}')
except Exception as e:
    print(f'\nFunnel SSL error: {e}')
