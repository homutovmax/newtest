"""Generate cover letter HTML files for each vacancy."""
import os, re
import html as html_mod
from generate_cover import generate_letter
from src.scrapers.shared import log


COVERS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _cover_html(title, company, location, salary, letter_text, category):
    ct_e = html_mod.escape(title)
    cc_e = html_mod.escape(company)
    cl_e = html_mod.escape(location) if location else ''
    cs_e = html_mod.escape(salary) if salary else ''
    lt = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', letter_text)
    lt = lt.replace('\n', '<br>')
    meta_line = ct_e + ' · ' + cc_e
    if cl_e:
        meta_line += ' · ' + cl_e
    if cs_e:
        meta_line += ' · ' + cs_e
    return f'''<!DOCTYPE html>
<html lang="ru"><head><meta charset="UTF-8"><title>Письмо: {ct_e}</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:'Segoe UI',Roboto,Arial,sans-serif; background:#f5f7fa; color:#1e293b; line-height:1.6; padding:20px; }}
.container {{ max-width:700px; margin:0 auto; }}
.card {{ background:#fff; border-radius:12px; padding:40px; box-shadow:0 1px 3px rgba(0,0,0,0.1); border:1px solid #e2e8f0; }}
.header {{ text-align:center; margin-bottom:24px; padding-bottom:20px; border-bottom:1px solid #e2e8f0; }}
.header h1 {{ font-size:20px; color:#2563eb; margin-bottom:4px; }}
.header .meta {{ font-size:13px; color:#64748b; }}
.actions {{ display:flex; gap:10px; justify-content:center; margin:24px 0 0; padding-top:20px; border-top:1px solid #e2e8f0; }}
.btn {{ display:inline-flex; align-items:center; gap:6px; padding:10px 20px; border-radius:8px; font-size:14px; font-weight:500; text-decoration:none; border:none; cursor:pointer; transition:all 0.15s; }}
.btn-primary {{ background:#0891b2; color:#fff; }}
.btn-primary:hover {{ background:#0e7490; }}
.btn-outline {{ background:#fff; color:#0891b2; border:1px solid #0891b2; }}
.btn-outline:hover {{ background:#ecfeff; }}
.letter-text {{ white-space:pre-wrap; font-size:15px; line-height:1.8; }}
.badge {{ display:inline-block; font-size:11px; padding:3px 10px; border-radius:6px; background:#f1f5f9; color:#64748b; }}
</style></head>
<body>
<div class="container">
  <div class="card">
    <div class="header">
      <h1>Сопроводительное письмо</h1>
      <div class="meta">{meta_line}</div>
      <div class="meta" style="margin-top:4px"><span class="badge">стиль: {html_mod.escape(category)}</span></div>
    </div>
    <div class="letter-text">{lt}</div>
    <div class="actions">
      <button class="btn btn-primary" onclick="copyLetter()">📋 Копировать</button>
      <button class="btn btn-primary" onclick="window.print()">🖨 Печать</button>
      <a class="btn btn-outline" href="vacancies_report.html">← Назад</a>
    </div>
  </div>
</div>
<script>
function copyLetter() {{ var t = document.querySelector('.letter-text').textContent;
  if (navigator.clipboard && navigator.clipboard.writeText) {{
    navigator.clipboard.writeText(t).then(function(){{ alert('Скопировано!'); }}).catch(function(){{ fallbackCopy(t); }});
  }} else {{ fallbackCopy(t); }}
  function fallbackCopy(text) {{ var ta = document.createElement('textarea'); ta.value = text;
    document.body.appendChild(ta); ta.select(); document.execCommand('copy');
    document.body.removeChild(ta); alert('Скопировано!');
  }}
}}
</script>
</body>
</html>'''


def generate(all_vacancies):
    generated = 0
    for i, v in enumerate(all_vacancies, 1):
        idx = f'v{i}'
        title = html_mod.unescape(str(v.get('title', '')))
        company = html_mod.unescape(str(v.get('company', '')))
        salary = html_mod.unescape(str(v.get('salary', '')))
        location = html_mod.unescape(str(v.get('location', '')))
        try:
            letter_text, category = generate_letter(title, company, 0, salary, location)
        except Exception:
            continue
        if not letter_text:
            continue
        cover_html = _cover_html(title, company, location, salary, letter_text, category)
        cover_path = os.path.join(COVERS_DIR, f'cover_{idx}.html')
        with open(cover_path, 'w', encoding='utf-8') as f:
            f.write(cover_html)
        generated += 1
    log(f'Сгенерировано cover-писем: {generated}/{len(all_vacancies)}')
