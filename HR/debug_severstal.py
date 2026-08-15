import requests
s = requests.Session()
s.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
r = s.get('https://career.severstal.com/vacancies/?page=23', timeout=15)
html = r.text

import re

# Simple extraction of card-vacancy blocks
blocks = re.findall(r'card-vacancy__title-text[^>]*>(.*?)</h3>.*?card-vacancy__place[^>]*>(.*?)</div>.*?card-vacancy__date[^>]*>(.*?)</time>', html, re.DOTALL)
print(f'Blocks found: {len(blocks)}')

for title, place, date in blocks[:3]:
    title = re.sub(r'<[^>]+>', '', title).strip()
    place = re.sub(r'<[^>]+>', '', place).strip()
    date = re.sub(r'<[^>]+>', '', date).strip()
    print(f'  title={title} | place={place} | date={date}')

# Also check if there are href links
links = re.findall(r'<a[^>]*href="(/vacancies/[^"]+)"[^>]*class="card-vacancy', html)
print(f'\nLinks found: {len(links)}')
for l in links[:3]:
    print(f'  {l}')
