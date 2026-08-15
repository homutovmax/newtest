import urllib.request, json

base = 'http://100.112.4.123:8000'
results = []

def check(name, url, expected_code=200):
    try:
        r = urllib.request.urlopen(base + url, timeout=10)
        ok = r.status == expected_code
        results.append((name, '✅' if ok else '❌', f'{r.status}, {len(r.read())}b'))
    except Exception as e:
        results.append((name, '❌', str(e)[:60]))

check('Health', '/health')
check('Report (all)', '/report')
check('Report (telecom)', '/report?tab=telecom')
check('Report (ai)', '/report?tab=ai')
check('Report (strategy)', '/report?tab=strategy')
check('Report (ba)', '/report?tab=ba')
check('Report (other)', '/report?tab=other')
check('Resume', '/resume?title=CTO&company=Test')
check('Resume (scenario=2)', '/resume?title=CTO+AI&company=Test&scenario=2')
check('Cover', '/cover/hh-133207087')
check('Cover (404)', '/cover/nonexistent', 404)
check('Analytics', '/analytics')
check('History', '/history')
check('Funnel HTTPS', 'https://ibox-z3-2.taila7bc1e.ts.net/health', 200)

print(f'\n=== UI TEST RESULTS ===')
for name, status, detail in results:
    print(f'  {status} {name}: {detail}')
print(f'\n{sum(1 for _,s,_ in results if "✅" in s)}/{len(results)} passed')
