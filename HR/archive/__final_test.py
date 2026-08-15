import socket

def fetch(url):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(10)
    s.connect(('100.112.4.123', 8000))
    s.send(f'GET {url} HTTP/1.0\r\nHost: test\r\n\r\n'.encode())
    resp = b''
    while True:
        c = s.recv(4096)
        if not c: break
        resp += c
    s.close()
    parts = resp.decode('utf-8', errors='replace').split('\r\n\r\n', 1)
    return parts[1] if len(parts) > 1 else ''

tabs = {'all': None, 'telecom': 'Telecom / IT', 'ai': 'AI / Product', 'strategy': 'Strategic', 'ba': 'Business Analysis', 'other': 'Other'}
results = {}
for tab, label in tabs.items():
    html = fetch(f'/report?tab={tab}')
    vcount = html.count('<div class="vacancy">')
    results[tab] = (len(html), vcount)
    tag_count = html.count('status-new')
    print(f'  {tab:10s} ({str(label or "Все"):20s}): {vcount:4d} вакансий, {len(html):>6d}b, new={tag_count}')

# Check for double new
for tab in ['all']:
    html = fetch(f'/report?tab={tab}')
    # Count single vacancy, check for double badges
    import re
    badges = re.findall(r'<span class="status-tag[^>]*>([^<]+)</span>', html)
    print(f'\nStatus badges sample: {badges[:10]}')
    vc = html.count('<div class="vacancy">')
    print(f'Total badges: {len(badges)}, vacancies: {vc}')

# Verify 
print('\nTab totals sum check:')
cats = [v for t, (_, v) in results.items() if t != 'all']
print(f'  Sum of category tabs: {sum(cats)}')
print(f'  All tab: {results["all"][1]}')
print(f'  {"Match!" if sum(cats) == results["all"][1] else "MISMATCH!"}')
