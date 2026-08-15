import json
with open('vacancies_history.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
found = []
for item in data.get('vacancies', []):
    t = item.get('title', '').lower()
    if 'персональн' in t or 'премьер' in t:
        found.append((item.get('title',''), item.get('company',''), item.get('status','')))
if found:
    for f_ in found:
        print(f'НАЙДЕН: {f_[0]} | {f_[1]} | {f_[2]}')
else:
    print('OK: ни персональн, ни премьер нет в активных')
