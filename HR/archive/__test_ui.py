import urllib.request, re

base = 'http://100.112.4.123:8000'

# 1. Check salaries in report
r = urllib.request.urlopen(base + '/report?tab=ai', timeout=10)
html = r.read().decode('utf-8', errors='replace')

salaries = re.findall(r'<div class="meta">(.*?)</div>', html, re.DOTALL)
print('Sample salaries (first 10):')
for s in salaries[:10]:
    clean = re.sub(r'<[^>]+>', '', s).strip()
    clean = re.sub(r'\s+', ' ', clean)
    print(f'  [{clean}]')

# 2. Check resume
r = urllib.request.urlopen(base + '/resume?title=CTO+AI&company=Test+Corp&scenario=2', timeout=10)
html = r.read().decode('utf-8', errors='replace')
print(f'\nResume ({len(html)} bytes):')
print(html[:400])

# 3. Check cover  
r = urllib.request.urlopen(base + '/cover/hh-133207087', timeout=10)
html = r.read().decode('utf-8', errors='replace')
print(f'\nCover ({len(html)} bytes): first 400 chars')
print(html[:400])

# 4. Check analytics
r = urllib.request.urlopen(base + '/analytics', timeout=10)
html = r.read().decode('utf-8', errors='replace')
print(f'\nAnalytics ({len(html)} bytes):')
print(html[:400])

# 5. Check history
r = urllib.request.urlopen(base + '/history', timeout=10)
html = r.read().decode('utf-8', errors='replace')
print(f'History ({len(html)} bytes)')

# 6. Check 404 for missing cover
try:
    r = urllib.request.urlopen(base + '/cover/nonexistent', timeout=5)
    print(f'\nMissing cover: {r.status}')
except urllib.error.HTTPError as e:
    print(f'\nMissing cover: {e.code} (expected)')

# 7. Check resume without params
r = urllib.request.urlopen(base + '/resume', timeout=5)
print(f'Resume empty: {r.status}')

print('\n=== DIAGNOSTIC DONE ===')
