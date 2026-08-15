#!/usr/bin/env python3
"""Telegram bot for HR project — polls commands and responds."""
import json, os, sys, re, time, traceback
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.parse import quote

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_DIR = os.environ.get('HR_HTML_DIR', os.path.join(BASE_DIR, '..', 'maximum64.beget.tech', 'public_html'))
TG_TOKEN = "CHANGE_ME"
PUBLIC_URL = os.environ.get('HR_PUBLIC_URL', 'http://maximum64.beget.tech')
STATE_FILE = os.path.join(BASE_DIR, 'tg_bot_state.json')
LOG_FILE = os.path.join(BASE_DIR, 'tg_bot.log')

def log(s):
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} {s}\n')

def tg_api(method, data):
    url = f'https://api.telegram.org/bot{TG_TOKEN}/{method}'
    body = json.dumps(data).encode('utf-8')
    req = Request(url, data=body, headers={'Content-Type': 'application/json'})
    try:
        resp = urlopen(req, timeout=15)
        r = json.loads(resp.read().decode('utf-8'))
        ok = r.get('ok')
        log(f'tg_api {method}: ok={ok} chat_id={data.get("chat_id")} text_len={len(data.get("text",""))}')
        if not ok:
            log(f'tg_api {method} NOT OK: {json.dumps(r, ensure_ascii=False)[:500]}')
        return r
    except Exception as e:
        log(f'tg_api {method} error: {e}')
        return None

def send_msg(chat_id, text, parse_mode='HTML'):
    return tg_api('sendMessage', {
        'chat_id': chat_id, 'text': text,
        'parse_mode': parse_mode, 'disable_web_page_preview': True
    })

def esc(s):
    return (s or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def get_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {'offset': 0}

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

def read_report_vacancies():
    """Parse latest report HTML for vacancy data."""
    report_path = os.path.join(HTML_DIR, 'vacancies_report.html')
    if not os.path.exists(report_path):
        return []
    with open(report_path, encoding='utf-8') as f:
        html = f.read()
    pattern = re.compile(
        r'data-title="([^"]*)"'
        r'\s*data-company="([^"]*)"'
        r'\s*data-salary="([^"]*)"'
        r'\s*data-location="([^"]*)"'
        r'\s*data-url="([^"]*)"'
    )
    vacs = []
    for m in pattern.finditer(html):
        vacs.append({
            'title': m.group(1), 'company': m.group(2),
            'salary': m.group(3), 'location': m.group(4), 'url': m.group(5),
        })
    return vacs

def read_history_new_today():
    """Return today's new vacancies from history JSON."""
    hist_path = os.path.join(BASE_DIR, 'vacancies_history.json')
    if not os.path.exists(hist_path):
        return []
    with open(hist_path, encoding='utf-8') as f:
        raw = json.load(f)
    if isinstance(raw, list):
        hist = {}
        for item in raw:
            k = item.get('key', f'hh-{item["id"]}' if item.get('source') == 'hh.ru' else f'habr-{item["id"]}')
            hist[k] = item
    else:
        hist = raw
    today_iso = datetime.now().strftime('%Y-%m-%d')
    new_today = []
    for key, v in hist.items():
        if v.get('status') == 'new' and v.get('firstSeen') == today_iso:
            new_today.append(v)
    return new_today

def generate_cover(title, company):
    """Import and call generate_letter directly."""
    try:
        sys.path.insert(0, HTML_DIR)
        sys.path.insert(0, BASE_DIR)
        from generate_cover import generate_letter
        return generate_letter(title, company, 0, '', '')
    except Exception as e:
        return None, str(e)

def cmd_start(chat_id, args):
    text = (
        '<b>🤖 HR Бот — Максим Хомутов</b>\n\n'
        'Помогаю с подборкой вакансий и сопроводительными письмами.\n\n'
        'Доступные команды:\n'
        '/new — новые вакансии за сегодня\n'
        '/report — ссылка на полную подборку\n'
        '/gen {название} // {компания} — сгенерировать сопроводительное\n'
        '/help — все команды'
    )
    send_msg(chat_id, text)

def cmd_help(chat_id, args):
    text = (
        '<b>📋 Команды бота</b>\n\n'
        '/start — приветствие\n'
        '/new — новые вакансии за сегодня (до 10)\n'
        '/report — ссылка на полную подборку\n'
        '/gen {название} // {компания} — сгенерировать сопроводительное\n'
        '   Пример: /gen Руководитель AI-продуктов // Сбер\n'
        '/help — это сообщение'
    )
    send_msg(chat_id, text)

def cmd_new(chat_id, args):
    new_today = read_history_new_today()
    if not new_today:
        send_msg(chat_id, 'Новых вакансий сегодня нет.')
        return
    lines = [f'<b>🆕 Новые вакансии ({len(new_today)})</b>', '']
    emoji = ['1️⃣','2️⃣','3️⃣','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣','9️⃣','🔟']
    for i, v in enumerate(new_today[:10]):
        n = emoji[i] if i < len(emoji) else f'{i+1}.'
        src = '🔵 Habr' if v.get('source') == 'Habr Career' else '🔴 hh'
        sal = f' · {esc(v.get("salary", ""))}' if v.get('salary') else ''
        loc = f' · {esc(v.get("location", ""))}' if v.get('location') else ''
        lines.append(f'{n} <a href="{esc(v.get("url", ""))}">{esc(v.get("title", ""))}</a>')
        lines.append(f'   {src} · {esc(v.get("company", ""))}{sal}{loc}')
    if len(new_today) > 10:
        lines.append(f'\n... и ещё {len(new_today) - 10}')
    lines.append(f'\nПодробнее: {PUBLIC_URL}/vacancies_report.html')
    send_msg(chat_id, '\n'.join(lines))

def cmd_report(chat_id, args):
    send_msg(chat_id, f'<a href="{PUBLIC_URL}/vacancies_report.html">📊 Полная подборка вакансий</a>')

def cmd_gen(chat_id, args):
    # Parse "title // company" format
    parts = args.split('//', 1)
    title = parts[0].strip() if parts else ''
    company = parts[1].strip() if len(parts) > 1 else ''
    if not title:
        send_msg(chat_id, 'Укажите название вакансии.\nПример: /gen Руководитель AI // Сбер')
        return
    send_msg(chat_id, '⏳ Генерирую сопроводительное...')
    text, category = generate_cover(title, company)
    if text is None:
        send_msg(chat_id, f'❌ Ошибка: {category}')
        return
    msg = f'<b>📄 Сопроводительное: {esc(title)}</b>'
    if company:
        msg += f' · {esc(company)}'
    if category:
        msg += f'\n<i>Стиль: {category}</i>'
    msg += f'\n\n{esc(text)}'
    send_msg(chat_id, msg)

COMMANDS = {
    '/start': cmd_start,
    '/help': cmd_help,
    '/new': cmd_new,
    '/today': cmd_new,
    '/report': cmd_report,
    '/gen': cmd_gen,
    '/generate': cmd_gen,
}

def process_update(upd):
    msg = upd.get('message', {})
    chat_id = msg.get('chat', {}).get('id')
    text = (msg.get('text') or '').strip()
    log(f'Update: chat={chat_id} text={text!r}')
    if not chat_id or not text:
        return
    parts = text.split(maxsplit=1)
    cmd = parts[0].lower() if parts else ''
    args = parts[1] if len(parts) > 1 else ''
    log(f'  Parsed: cmd={cmd!r} args={args!r}')
    handler = COMMANDS.get(cmd)
    if handler:
        log(f'  Executing handler for {cmd}')
        try:
            handler(chat_id, args)
            log(f'  Handler {cmd} OK')
        except Exception as e:
            log(f'  Handler {cmd} error: {e}')
            log(traceback.format_exc())

def main():
    log('=== BOT START ===')
    state = get_state()
    offset = state.get('offset', 0)
    log(f'Offset: {offset}')
    deadline = time.time() + 110
    while time.time() < deadline:
        updates = tg_api('getUpdates', {'offset': offset, 'timeout': 55})
        if not updates or not updates.get('ok'):
            break
        for upd in updates.get('result', []):
            process_update(upd)
            new_offset = upd['update_id'] + 1
            if new_offset > offset:
                offset = new_offset
        state['offset'] = offset
        save_state(state)
    log(f'Final offset: {offset}')
    log('=== BOT END ===')

if __name__ == '__main__':
    main()
