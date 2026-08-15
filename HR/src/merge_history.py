"""Merge scraped vacancies into history JSON."""
import json, os
from datetime import datetime
from src.scrapers.shared import log


HISTORY_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "vacancies_history.json")


def merge(all_vacancies):
    today_iso = datetime.now().strftime('%Y-%m-%d')

    history = {}
    if os.path.exists(HISTORY_PATH):
        try:
            with open(HISTORY_PATH, 'r', encoding='utf-8-sig') as f:
                raw = json.load(f)
            if isinstance(raw, list):
                for item in raw:
                    src = item.get('source', '')
                    raw_id = item.get('id', '')
                    if src == 'Habr Career':
                        k = item.get('key', raw_id if raw_id.startswith('habr-') else f'habr-{raw_id}')
                    elif src == 'Сбер (rabota.sber.ru)':
                        k = item.get('key', raw_id if raw_id.startswith('sber-') else f'sber-{raw_id}')
                    else:
                        k = item.get('key', raw_id if raw_id.startswith('hh-') else f'hh-{raw_id}')
                    history[k] = item
            else:
                history = raw
        except Exception as e:
            log(f'Ошибка загрузки истории: {e}')

    active_keys = set()
    for v in all_vacancies:
        key = v['id']
        active_keys.add(key)
        if key in history:
            history[key]['lastSeen'] = today_iso
            if history[key].get('firstSeen') != today_iso:
                history[key]['status'] = 'active'
            history[key]['title'] = v.get('title', '')
            history[key]['company'] = v.get('company', '')
            history[key]['salary'] = v.get('salary', '')
            history[key]['location'] = v.get('location', '')
        else:
            history[key] = {
                'id': v.get('id', ''), 'source': v.get('source', ''),
                'title': v.get('title', ''), 'company': v.get('company', ''),
                'salary': v.get('salary', ''), 'location': v.get('location', ''),
                'url': v.get('url', ''),
                'firstSeen': today_iso, 'lastSeen': today_iso,
                'status': 'new',
            }

    for key in list(history.keys()):
        if key not in active_keys and history[key].get('status') != 'closed':
            history[key]['status'] = 'closed'
            history[key]['lastSeen'] = today_iso

    with open(HISTORY_PATH, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    log(f'История сохранена: {len(history)} записей')
