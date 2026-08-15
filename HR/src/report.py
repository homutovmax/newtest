"""Generate HTML reports from history JSON."""
import os, sys, json, re
import html as html_mod
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scrapers.shared import log, esc, format_date_ru
from src.classifier import classify_title

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HISTORY_PATH = os.path.join(BASE_DIR, "vacancies_history.json")
REPORT_PATH = os.path.join(BASE_DIR, "vacancies_report.html")
HISTORY_PAGE_PATH = os.path.join(BASE_DIR, "vacancies_history.html")

MONTHS_RU = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']


def _load_history():
    if not os.path.exists(HISTORY_PATH):
        return {}, []
    with open(HISTORY_PATH, 'r', encoding='utf-8-sig') as f:
        raw = json.load(f)
    if isinstance(raw, list):
        history = {}
        for item in raw:
            k = item.get('key', item.get('id', ''))
            history[k] = item
    else:
        history = raw
    return history, []


def _build_vacancy_list(history):
    today_iso = datetime.now().strftime('%Y-%m-%d')
    vacs = []
    for key, v in history.items():
        if v.get('status') in ('new', 'active'):
            vacs.append({
                'Id': v.get('id', ''),
                'Title': v.get('title', ''),
                'Company': v.get('company', ''),
                'Salary': v.get('salary', ''),
                'Location': v.get('location', ''),
                'Url': v.get('url', ''),
                'Source': v.get('source', ''),
                'firstSeen': v.get('firstSeen', ''),
            })
    vacs.sort(key=lambda x: (
        0 if x.get('firstSeen') == today_iso else 1,
        0 if x.get('Salary') else 1
    ))
    for v in vacs:
        v['Scenario'] = classify_title(v.get('Title', ''))
    return vacs


def gen_report_html():
    today = datetime.now()
    today_iso = today.strftime('%Y-%m-%d')
    today_str = format_date_ru(today)

    history, _ = _load_history()
    all_vacancies = _build_vacancy_list(history)

    hh_count = sum(1 for v in all_vacancies if v.get('Source') == 'hh.ru')
    habr_count = sum(1 for v in all_vacancies if v.get('Source') == 'Habr Career')
    sber_count = sum(1 for v in all_vacancies if v.get('Source') == 'Сбер (rabota.sber.ru)')
    portal_count = len(all_vacancies) - hh_count - habr_count - sber_count
    new_today = [v for v in all_vacancies if v.get('firstSeen') == today_iso]

    lines = []
    lines.append(f'''<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Подборка вакансий — {today_str}</title>
<style>
  :root {{ --bg: #f5f7fa; --card: #ffffff; --accent: #2563eb; --green: #059669; --text: #1e293b; --muted: #64748b; --border: #e2e8f0; }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background: var(--bg); color: var(--text); line-height: 1.5; }}
  .header {{ background: linear-gradient(135deg, #1e293b, #334155); color: #fff; padding: 40px 24px; text-align: center; }}
  .header h1 {{ font-size: 28px; margin-bottom: 8px; }}
  .header p {{ color: #94a3b8; font-size: 14px; }}
  .header .date {{ margin-top: 12px; font-size: 13px; color: #94a3b8; }}
  .update-badge {{ display: inline-block; margin-top: 8px; padding: 4px 14px; background: #059669; color: #fff; border-radius: 20px; font-size: 12px; font-weight: 500; }}
  .nav-links {{ display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; margin-top: 8px; }}
  .nav-links a {{ color: #93c5fd; font-size: 13px; }}
  .container {{ max-width: 960px; margin: 0 auto; padding: 24px 16px; }}
  .stats {{ display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 20px; }}
  .stat-card {{ flex: 1; min-width: 140px; background: var(--card); border-radius: 10px; padding: 16px; text-align: center; border: 1px solid var(--border); }}
  .stat-card .num {{ font-size: 28px; font-weight: 700; }}
  .stat-card .label {{ font-size: 13px; color: var(--muted); margin-top: 4px; }}
  .stat-card.new .num {{ color: var(--green); }}
  .stat-card.hh .num {{ color: var(--accent); }}
  .stat-card.habr .num {{ color: #d97706; }}
  .stat-card.portal .num {{ color: #7c3aed; }}
  .stat-card.sber .num {{ color: #22c55e; }}
  .stat-card.total .num {{ color: var(--text); }}
  .vacancy {{ background: var(--card); border-radius: 12px; padding: 20px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); border: 1px solid var(--border); transition: box-shadow 0.2s; }}
  .vacancy:hover {{ box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
  .vacancy-header {{ display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; flex-wrap: wrap; margin-bottom: 8px; }}
  .vacancy-title {{ font-size: 18px; font-weight: 600; color: var(--accent); text-decoration: none; }}
  .vacancy-title:hover {{ text-decoration: underline; }}
  .vacancy-company {{ font-size: 15px; color: var(--text); font-weight: 500; }}
  .vacancy-meta {{ display: flex; flex-wrap: wrap; gap: 8px; margin: 8px 0 12px; }}
  .meta-tag {{ display: inline-flex; align-items: center; font-size: 13px; color: var(--muted); background: #f1f5f9; padding: 4px 10px; border-radius: 6px; }}
  .meta-tag.salary {{ color: var(--green); font-weight: 600; background: #ecfdf5; }}
  .meta-tag.habr {{ background: #fef3c7; color: #92400e; }}
  .meta-tag.hh {{ background: #dbeafe; color: #1e40af; }}
  .meta-tag.sber {{ background: #dcfce7; color: #166534; }}
  .vacancy-actions {{ display: flex; gap: 8px; flex-wrap: wrap; margin-top: 12px; }}
  .btn {{ display: inline-flex; align-items: center; gap: 6px; padding: 8px 16px; border-radius: 8px; font-size: 14px; font-weight: 500; text-decoration: none; border: none; cursor: pointer; transition: all 0.15s; }}
  .btn-primary {{ background: var(--accent); color: #fff; }}
  .btn-primary:hover {{ background: #1d4ed8; }}
  .btn-cover {{ background: #7c3aed; color: #fff; }}
  .btn-cover:hover {{ background: #6d28d9; }}
  .btn-resume {{ background: #0891b2; color: #fff; }}
  .btn-resume:hover {{ background: #0e7490; }}
  .btn-telegram {{ background: #059669; color: #fff; }}
  .btn-telegram:hover {{ background: #047857; }}
  .toast {{ position: fixed; bottom: 24px; right: 24px; background: #1e293b; color: #fff; padding: 12px 20px; border-radius: 10px; font-size: 14px; box-shadow: 0 4px 12px rgba(0,0,0,0.2); opacity: 0; transform: translateY(20px); transition: all 0.3s; pointer-events: none; z-index: 100; }}
  .toast.show {{ opacity: 1; transform: translateY(0); }}
  .status-badge {{ display: inline-block; font-size: 12px; padding: 3px 8px; border-radius: 6px; font-weight: 500; background: #dcfce7; color: #166534; }}
  @media (max-width: 640px) {{ .vacancy-actions {{ flex-direction: column; }} .btn {{ justify-content: center; }} .stats {{ flex-direction: column; }} }}
  .empty-note {{ background: #f8fafc; border: 1px dashed var(--border); border-radius: 10px; padding: 20px; text-align: center; color: var(--muted); font-size: 14px; margin-bottom: 16px; }}
  .empty-note a {{ color: var(--accent); }}
  .last-updated {{ text-align: center; color: var(--muted); font-size: 12px; margin: 24px 0; }}
  .tabs {{ display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 20px; }}
  .tab-btn {{ padding: 8px 16px; border-radius: 8px; border: 1px solid var(--border); background: var(--card); color: var(--muted); cursor: pointer; font-size: 14px; font-weight: 500; transition: all 0.15s; }}
  .tab-btn:hover {{ border-color: var(--accent); color: var(--accent); }}
  .tab-btn.active {{ background: var(--accent); color: #fff; border-color: var(--accent); }}
  .tab-count {{ display: inline-block; font-size: 11px; padding: 1px 6px; border-radius: 10px; background: rgba(255,255,255,0.2); margin-left: 4px; }}
  .tab-content {{ display: none; }}
</style>
</head>
<body>
<div class="header">
  <h1>Подборка вакансий</h1>
  <p>Для Максима Хомутова — Head of Direction / Head of AI / Transformation Director</p>
  <div class="date">Обновлено {today_str} · Москва · hh.ru + Habr Career + Сбер</div>
  <div class="update-badge">ежедневно в 10:00 и 14:00</div>
  <div class="nav-links">
    <a href="vacancies_history.html">📊 История вакансий →</a>
  </div>
</div>
<div class="container">
  <div class="stats">
    <div class="stat-card total"><div class="num">{len(all_vacancies)}</div><div class="label">Всего</div></div>
    <div class="stat-card hh"><div class="num">{hh_count}</div><div class="label">hh.ru</div></div>
    <div class="stat-card habr"><div class="num">{habr_count}</div><div class="label">Habr Career</div></div>
    <div class="stat-card sber"><div class="num">{sber_count}</div><div class="label">Сбер</div></div>
    <div class="stat-card new"><div class="num">{len(new_today)}</div><div class="label">Новых сегодня</div></div>
  </div>

  <!-- Tabs -->
  <div class="tabs">
    <button class="tab-btn active" data-tab="all" onclick="switchTab('all')">📋 Все <span class="tab-count">{len(all_vacancies)}</span></button>
    <button class="tab-btn" data-tab="telecom" onclick="switchTab('telecom')">📡 Telecom / IT</button>
    <button class="tab-btn" data-tab="ai_product" onclick="switchTab('ai_product')">🤖 AI / Product</button>
    <button class="tab-btn" data-tab="strategy" onclick="switchTab('strategy')">🎯 Strategic</button>
    <button class="tab-btn" data-tab="ba" onclick="switchTab('ba')">📊 Business Analysis</button>
    <button class="tab-btn" data-tab="other" onclick="switchTab('other')">📁 Other</button>
  </div>''')

    tab_defs = {
        "all": {"label": "Все", "vacancies": list(enumerate(all_vacancies, 1))},
        "telecom": {"label": "Telecom / IT", "vacancies": [(i+1, v) for i, v in enumerate(all_vacancies) if v.get('Scenario') == 'telecom']},
        "ai_product": {"label": "AI / Product", "vacancies": [(i+1, v) for i, v in enumerate(all_vacancies) if v.get('Scenario') == 'ai_product']},
        "strategy": {"label": "Strategic", "vacancies": [(i+1, v) for i, v in enumerate(all_vacancies) if v.get('Scenario') == 'strategy']},
        "ba": {"label": "Business Analysis", "vacancies": [(i+1, v) for i, v in enumerate(all_vacancies) if v.get('Scenario') == 'ba']},
        "other": {"label": "Прочее", "vacancies": [(i+1, v) for i, v in enumerate(all_vacancies) if v.get('Scenario', '') not in ('telecom', 'ai_product', 'strategy', 'ba')]},
    }

    for tab_id, tab_data in tab_defs.items():
        show = ' style="display:block"' if tab_id == 'all' else ''
        lines.append(f'<div class="tab-content" id="tab-{tab_id}"{show}>')
        vacs = tab_data["vacancies"]
        if not vacs:
            lines.append('<div class="empty-note">Вакансий в этой категории пока нет</div>')
        else:
            for idx, v in vacs:
                th = esc(v.get('Title', ''))
                tc = esc(v.get('Company', ''))
                tl = esc(v.get('Location', ''))
                ts = esc(v.get('Salary', ''))
                salary_display = ts
                salary_tag = f'<span class="meta-tag salary">{salary_display}</span>' if salary_display else ''
                loc_tag = f'<span class="meta-tag">{tl}</span>'
                if v.get('Source') == 'Habr Career':
                    src_class = 'habr'
                    btn_label = 'Открыть на Habr'
                    site_id = v.get('Id', '').replace('habr-', '')
                elif v.get('Source') == 'Сбер (rabota.sber.ru)':
                    src_class = 'sber'
                    btn_label = 'Открыть на rabota.sber.ru'
                    site_id = v.get('Id', '')
                else:
                    src_class = 'hh'
                    btn_label = 'Открыть на hh.ru'
                    site_id = v.get('Id', '')
                src_tag = f'<span class="meta-tag {src_class}">{esc(v.get("Source", ""))}</span>'
                company_display = tc if tc else v.get('Source', '')
                new_badge = '<span class="status-badge">новое</span>' if v.get('firstSeen') == today_iso else ''
                salary_attr = ts
                lines.append(f'''  <div class="vacancy" data-vacancy-id="v{idx}" data-site="{esc(v.get('Source', ''))}" data-site-id="{site_id}" data-title="{th}" data-company="{company_display}" data-salary="{salary_attr}" data-location="{tl}" data-url="{esc(v.get('Url', ''))}">
    <div class="vacancy-header">
      <div>
        <a class="vacancy-title" href="{esc(v.get('Url', ''))}" target="_blank">{th}</a>
        <div class="vacancy-company">{company_display}</div>
      </div>
      {new_badge}
    </div>
    <div class="vacancy-meta">
      {loc_tag}
      {salary_tag}
      {src_tag}
    </div>
    <div class="vacancy-actions">
      <a class="btn btn-primary" href="{esc(v.get('Url', ''))}" target="_blank">{btn_label}</a>
      <a class="btn btn-cover" href="cover_v{idx}.html" target="_blank">Сопроводительное</a>
      <button class="btn btn-resume" onclick="openResume('v{idx}')">Резюме</button>
    </div>
  </div>''')
        lines.append('</div>')

    lines.append(f'''</div>
<div class="toast" id="toast"></div>
<script>
function switchTab(tabId) {{
  document.querySelectorAll('.tab-content').forEach(function(el) {{ el.style.display = 'none'; }});
  document.querySelectorAll('.tab-btn').forEach(function(el) {{ el.classList.remove('active'); }});
  document.getElementById('tab-' + tabId).style.display = 'block';
  document.querySelector('.tab-btn[data-tab="' + tabId + '"]').classList.add('active');
}}
function openResume(id) {{
  var el = document.querySelector('[data-vacancy-id="' + id + '"]');
  if (!el) return;
  var title = encodeURIComponent(el.dataset.title || id);
  var company = encodeURIComponent(el.dataset.company || '');
  var site = encodeURIComponent(el.dataset.site || '');
  var siteId = encodeURIComponent(el.dataset.siteId || '');
  var salary = encodeURIComponent(el.dataset.salary || '');
  var location = encodeURIComponent(el.dataset.location || '');
  var url = encodeURIComponent(el.dataset.url || '');
  window.open('resume.php?title=' + title + '&company=' + company + '&site=' + site + '&id=' + siteId + '&url=' + url + '&salary=' + salary + '&location=' + location, '_blank');
}}
</script>
</body>
</html>''')
    return '\n'.join(lines)


def gen_hist_html():
    today = datetime.now()
    today_iso = today.strftime('%Y-%m-%d')

    history, _ = _load_history()
    new_today_list = [v for v in history.values() if v.get('status') == 'new' and v.get('firstSeen') == today_iso]
    active_now = [v for v in history.values() if v.get('status') in ('active', 'new')]
    closed_today = [v for v in history.values() if v.get('status') == 'closed' and v.get('lastSeen') == today_iso]
    closed_only = [v for v in history.values() if v.get('status') == 'closed']

    lines = []
    lines.append(f'''<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>История вакансий — {today_iso}</title>
<style>
  :root {{ --bg: #f5f7fa; --card: #ffffff; --accent: #2563eb; --green: #059669; --red: #dc2626; --amber: #d97706; --text: #1e293b; --muted: #64748b; --border: #e2e8f0; }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: var(--bg); color: var(--text); line-height: 1.5; }}
  .header {{ background: linear-gradient(135deg, #1e293b, #334155); color: #fff; padding: 32px 24px; text-align: center; }}
  .header h1 {{ font-size: 26px; margin-bottom: 8px; }}
  .header p {{ color: #94a3b8; font-size: 14px; }}
  .container {{ max-width: 960px; margin: 0 auto; padding: 24px 16px; }}
  .stats {{ display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 20px; }}
  .stat-card {{ flex: 1; min-width: 140px; background: var(--card); border-radius: 10px; padding: 16px; text-align: center; border: 1px solid var(--border); }}
  .stat-card .num {{ font-size: 28px; font-weight: 700; }}
  .stat-card .label {{ font-size: 13px; color: var(--muted); margin-top: 4px; }}
  .stat-card.new .num {{ color: var(--green); }}
  .stat-card.active .num {{ color: var(--accent); }}
  .stat-card.closed .num {{ color: var(--red); }}
  .stat-card.total .num {{ color: var(--text); }}
  .section-title {{ font-size: 18px; font-weight: 600; margin: 24px 0 12px; display: flex; align-items: center; gap: 8px; }}
  .section-title .badge {{ font-size: 12px; background: var(--border); padding: 2px 10px; border-radius: 12px; font-weight: 500; }}
  .vacancy {{ background: var(--card); border-radius: 10px; padding: 16px; margin-bottom: 10px; border: 1px solid var(--border); display: flex; gap: 12px; align-items: flex-start; }}
  .vacancy.new {{ border-left: 4px solid var(--green); }}
  .vacancy.active {{ border-left: 4px solid var(--accent); }}
  .vacancy.closed {{ border-left: 4px solid var(--red); opacity: 0.7; }}
  .vacancy-info {{ flex: 1; }}
  .vacancy-title {{ font-size: 15px; font-weight: 600; color: var(--accent); text-decoration: none; }}
  .vacancy-company {{ font-size: 13px; color: var(--text); }}
  .vacancy-dates {{ font-size: 12px; color: var(--muted); margin-top: 4px; }}
  .vacancy-meta {{ font-size: 12px; color: var(--muted); margin-top: 2px; }}
  .status-tag {{ display: inline-block; font-size: 11px; padding: 2px 8px; border-radius: 10px; font-weight: 500; }}
  .status-tag.new {{ background: #dcfce7; color: #166534; }}
  .status-tag.active {{ background: #dbeafe; color: #1e40af; }}
  .status-tag.closed {{ background: #fee2e2; color: #991b1b; }}
  .nav-link {{ display: inline-block; margin-top: 20px; color: var(--accent); font-size: 14px; }}
  @media (max-width: 640px) {{ .stats {{ flex-direction: column; }} }}
</style>
</head>
<body>
<div class="header">
  <h1>📊 История вакансий</h1>
  <p>Отслеживание появления и закрытия вакансий для Максима Хомутова</p>
</div>
<div class="container">
  <div class="stats">
    <div class="stat-card new"><div class="num">{len(new_today_list)}</div><div class="label">Новых сегодня</div></div>
    <div class="stat-card active"><div class="num">{len(active_now)}</div><div class="label">Активных</div></div>
    <div class="stat-card closed"><div class="num">{len(closed_today)}</div><div class="label">Закрыто сегодня</div></div>
    <div class="stat-card total"><div class="num">{len(history)}</div><div class="label">Всего в истории</div></div>
  </div>''')

    def vac_card(v, status_class, status_label):
        th = esc(str(v.get('title', '')))
        tc = esc(str(v.get('company', '')))
        ts = esc(str(v.get('salary', '')))
        tl = esc(str(v.get('location', '')))
        meta_parts = [p for p in [ts, tl] if p]
        meta_str = f' · {" · ".join(meta_parts)}' if meta_parts else ''
        url = v.get('url', '')
        first = v.get('firstSeen', '')
        last = v.get('lastSeen', '')
        return f'''  <div class="vacancy {status_class}">
    <div><span class="status-tag {status_class}">{status_label}</span></div>
    <div class="vacancy-info">
      <a class="vacancy-title" href="{url}" target="_blank">{th}</a>
      <div class="vacancy-company">{tc} · {v.get('source', '')}</div>
      <div class="vacancy-meta">{meta_str}</div>
      <div class="vacancy-dates">{'Впервые: ' + first if status_class == 'new' else 'С ' + first + ' · последний раз ' + last if status_class == 'active' else 'Была: с ' + first + ' до ' + last}</div>
    </div>
  </div>'''

    lines.append(f'<div class="section-title">🆕 Новые сегодня <span class="badge">{len(new_today_list)}</span></div>')
    if not new_today_list:
        lines.append('<p style="color: var(--muted); font-size: 14px;">Новых вакансий сегодня нет</p>')
    else:
        for v in sorted(new_today_list, key=lambda x: (x.get('source', ''), x.get('title', ''))):
            lines.append(vac_card(v, 'new', 'NEW'))

    active_list = [v for v in active_now if v.get('status') == 'active']
    lines.append(f'<div class="section-title">✅ Активные <span class="badge">{len(active_list)}</span></div>')
    if not active_list:
        lines.append('<p style="color: var(--muted); font-size: 14px;">Нет активных вакансий</p>')
    else:
        for v in sorted(active_list, key=lambda x: (x.get('source', ''), x.get('title', ''))):
            lines.append(vac_card(v, 'active', 'активна'))

    lines.append(f'<div class="section-title">❌ Закрыто сегодня <span class="badge">{len(closed_today)}</span></div>')
    if not closed_today:
        lines.append('<p style="color: var(--muted); font-size: 14px;">Закрытых сегодня нет</p>')
    else:
        for v in sorted(closed_today, key=lambda x: (x.get('source', ''), x.get('title', ''))):
            lines.append(vac_card(v, 'closed', 'закрыта'))

    older = [v for v in closed_only if v.get('lastSeen') != today_iso]
    older = sorted(older, key=lambda x: (x.get('lastSeen', ''), x.get('title', '')), reverse=True)[:50]
    if older:
        lines.append(f'<div class="section-title">📜 Ранее закрытые <span class="badge">{len(older)} из {len(closed_only)}</span></div>')
        for v in older:
            lines.append(vac_card(v, 'closed', 'закрыта'))

    lines.append(f'''  <div style="text-align: center; margin: 32px 0;">
    <a class="nav-link" href="vacancies_report.html">← К подборке вакансий</a>
  </div>
  <div style="text-align: center; color: var(--muted); font-size: 12px;">
    Обновлено {today_iso} в 10:00 и 14:00
  </div>
</div>
</body>
</html>''')
    return '\n'.join(lines)


def generate():
    log("Генерация отчётов...")
    report_html = gen_report_html()
    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        f.write(report_html)
    hist_html = gen_hist_html()
    with open(HISTORY_PAGE_PATH, 'w', encoding='utf-8') as f:
        f.write(hist_html)
    log(f"Отчёт: {REPORT_PATH}")
    log(f"История: {HISTORY_PAGE_PATH}")


if __name__ == "__main__":
    generate()
