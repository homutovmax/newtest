#!/usr/bin/env python3
"""Автоматическая аналитика после генерации отчёта + HTML-отчёт об ошибках."""
import json, re, os, sys, html as html_mod
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from generate_cover import classify_title

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_JSON = os.path.join(BASE_DIR, 'vacancies_history.json')
REPORT_HTML = os.path.join(BASE_DIR, 'vacancies_report.html')
ANALYTICS_REPORT = os.path.join(BASE_DIR, 'vacancies_analytics.html')

issues = []

def issue(msg, suggestion, severity='warning'):
    issues.append({'msg': msg, 'suggestion': suggestion, 'severity': severity})

# 1. EXCLUDE_WORDS — проверить, не просочились ли
EXCLUDE_CHECK = ['персональн', 'премьер', 'ассистент', 'помощник', 'личн']
with open(REPORT_HTML, 'r', encoding='utf-8') as f:
    html_content = f.read()
found_words = [w for w in EXCLUDE_CHECK if w.lower() in html_content.lower()]
if found_words:
    issue(
        f'Найдены exclude-слова в отчёте: {", ".join(found_words)}',
        'Добавить найденные слова в EXCLUDE_WORDS в update_vacancies.py и перезапустить.'
    )

# 2. Dummy-зарплаты 100
dummy = re.findall(r'(?<!\d)100\s*[₽р]', html_content)
if dummy:
    issue(
        f'Найдено {len(dummy)} dummy-зарплат(ы) "100 ₽"',
        'Проверить salary_filter() в update_vacancies.py — regex не срабатывает.'
    )

# 3. Double-prefix в истории
with open(HISTORY_JSON, 'r', encoding='utf-8') as f:
    hist = json.load(f)
double = [k for k in hist if 'habr-habr' in k]
if double:
    issue(
        f'Найдено {len(double)} double-prefix ключей habr-habr-',
        'Удалить проблемные ключи из vacancies_history.json и перезапустить. '
        'Причина: код в update_vacancies.py добавлял habr- к id, который уже содержал habr-.'
    )

# 4. Классификация — smoke test
smoke = [
    ('Системный аналитик', 'ba', 'BA keywords (analyst, аналитик, требований)'),
    ('Head of AI', 'ai_product', 'AI keywords (ai, head, product)'),
    ('Директор по цифровой трансформации', 'strategy', 'Strategy keywords (цифровая + трансформация)'),
    ('CTO телеком', 'telecom', 'Telecom keywords (cto, телеком)'),
    ('Продавец', 'unknown', 'Нет совпадений → unknown'),
]
for title, expected, reason in smoke:
    result = classify_title(title)
    if result != expected:
        issue(
            f'classify_title({title!r}) = {result}, ожидался {expected}',
            f'Проверить ключевые слова в classify_title() generate_cover.py. Ожидание: {reason}'
        )

# 5. Пустой заголовок
if classify_title('') != 'unknown':
    issue(
        'classify_title("") не возвращает unknown',
        'Проверить ba_score > 0 and ba_score >= max() в classify_title() generate_cover.py.'
    )

# 6. Счётчики
total = len(hist)
ok = len(issues) == 0

# 7. Генерация HTML-отчёта
severity_colors = {'warning': '#f0ad4e', 'error': '#d9534f', 'info': '#5bc0de'}

html_report = f'''<!DOCTYPE html>
<html lang="ru">
<head><meta charset="utf-8"><title>Аналитика вакансий</title>
<style>
body{{font-family:-apple-system,BlinkMacSystemFont,sans-serif;max-width:800px;margin:40px auto;padding:0 20px;color:#333;line-height:1.5}}
h1{{color:#2c3e50;border-bottom:2px solid #eee;padding-bottom:10px}}
.summary{{font-size:1.2em;padding:15px;border-radius:8px;margin:20px 0}}
.summary.pass{{background:#d4edda;color:#155724;border:1px solid #c3e6cb}}
.summary.fail{{background:#f8d7da;color:#721c24;border:1px solid #f5c6cb}}
.issue{{margin:15px 0;padding:15px;border-radius:8px;border-left:5px solid #ccc}}
.issue.warning{{border-left-color:#f0ad4e;background:#fffaf0}}
.issue.error{{border-left-color:#d9534f;background:#fff5f5}}
.issue h3{{margin:0 0 8px;font-size:1em}}
.issue .suggestion{{margin:8px 0 0;padding:8px 12px;background:#f8f9fa;border-radius:4px;font-size:0.9em;color:#555}}
.issue .suggestion strong{{color:#333}}
.meta{{color:#999;font-size:0.85em;margin-top:20px}}
ul{{margin:4px 0;padding-left:20px}}
pre{{background:#f5f5f5;padding:8px;border-radius:4px;overflow-x:auto}}
</style>
</head>
<body>
<h1>Аналитика подборки вакансий</h1>
<p>Отчёт от {datetime.now().strftime('%d.%m.%Y %H:%M')}</p>
<div class="summary {'' if ok else 'fail' if issues else 'pass'}">
{"✓ Все проверки пройдены" if ok else "✗ Найдены проблемы: требуется исправление"}
</div>
<p>Всего записей в истории: <strong>{total}</strong></p>
'''

if issues:
    html_report += '<h2>Проблемы</h2>'
    for i, iss in enumerate(issues, 1):
        sev = iss['severity']
        html_report += f'''
<div class="issue {sev}">
<h3>{i}. {html_mod.escape(iss['msg'])}</h3>
<div class="suggestion"><strong>Устранение:</strong> {html_mod.escape(iss['suggestion'])}</div>
</div>'''

html_report += '''
<div class="meta">
<a href="vacancies_report.html">Вернуться к подборке</a>
</div>
</body>
</html>'''

with open(ANALYTICS_REPORT, 'w', encoding='utf-8') as f:
    f.write(html_report)

# 8. Вывод в stdout (для лога)
if issues:
    print(f'АНАЛИТИКА: {len(issues)} проблем(а/ы) — см. vacancies_analytics.html')
    for iss in issues:
        print(f'  ✗ {iss["msg"]}')
    sys.exit(1)
else:
    print(f'Вакансий: {total}, все проверки пройдены — vacancies_analytics.html')
