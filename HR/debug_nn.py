import requests
s = requests.Session()
s.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})

# Check NorNickel page 1
r = s.get('https://career.nornickel.ru/vacancies', timeout=30)
html = r.text
print('=== NorNickel page 1 ===')
print('filter-app__result count:', html.count('filter-app__result'))
print('filter-app__result-name count:', html.count('filter-app__result-name'))
print('vacancy-card count:', html.count('vacancy-card'))
print('total length:', len(html))

# Check for any vacancy-like patterns
for name, pattern in [('filter-app__result', 'filter-app__result'), 
                       ('vacancy-', 'vacancy-'),
                       ('vacancy-card', 'vacancy-card'),
                       ('job-item', 'job-item'),
                       ('data-get', 'data-get="/api')]:
    idx = html.find(pattern)
    if idx >= 0:
        print(f'First "{name}" at {idx}: {html[idx:idx+250]}')
    else:
        print(f'No "{name}" found')

# Check page 2
r2 = s.get('https://career.nornickel.ru/vacancies?page=2', timeout=30)
html2 = r2.text
print('\n=== NorNickel page 2 ===')
print('filter-app__result count:', html2.count('filter-app__result'))
print('total length:', len(html2))
