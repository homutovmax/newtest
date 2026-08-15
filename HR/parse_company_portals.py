#!/usr/bin/env python3
# parse_company_portals.py — Парсинг карьерных порталов целевых компаний

import requests
import re
import time
from datetime import datetime

session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})

EXCLUDE_WORDS = [
    'продаж', 'sales', 'developer', 'support', 'техподдержк', 'разработчик', 'специалист', '1С',
    'hr-', 'hr ', 'hr_manager', 'консультант', 'оператор', 'водитель', 'продавец', 'фармацевт',
    'администратор', 'официант', 'курьер', 'доставк', 'уборщик', 'мерчендайзер',
    'страхование', 'агент', 'кассир', 'грузчик', 'комплектовщик', 'сборщик',
    'охранник', 'упаковщик', 'промоутер', 'андеррайтер',
    'брокер по работе с клиентами', 'менеджер по работе с клиентами',
    'стоматолог', 'ортодонт', 'хирург', 'терапевт', 'медицин', 'врач', 'медсестр',
    'маркетолог', 'реклам', 'повар', 'юрист', 'бухгалтер', 'экономист',
    'дизайнер', 'стилист', 'косметолог', 'фитнес', 'тренер',
    'секретарь', 'дворник', 'горничн', 'бармен', 'адвокат', 'нотариус',
    'электрик', 'сантехник', 'строител', 'инженер-проектировщик',
    'логист', 'кладовщик', 'инспектор', 'контролер',
    'воспитател', 'учител', 'преподавател', 'психолог',
    'пищев', 'шоколад', 'морожен', 'кондитер', 'упаковк',
    'биотехнолог', 'производств', 'фабрик', 'недвижимость',
    'бренд-шеф', 'категорийн', 'младший', 'ключевых клиентов',
    'привлечени', 'инвестици', 'брокер',
    'персональн', 'премьер', 'ассистент', 'помощник', 'личн'
]

def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    print(f'  [{ts}] {msg}', flush=True)

def _fetch(url):
    try:
        r = session.get(url, timeout=30)
        r.raise_for_status()
        return r.text
    except Exception as e:
        log(f'  Ошибка HTTP: {e}')
    return None

def _fetch_json(url):
    try:
        r = session.get(url, timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        log(f'  Ошибка JSON: {e}')
    return None

def is_moscow_spb(loc):
    if not loc:
        return True
    l = loc.lower()
    if 'москв' in l or 'санкт-петербург' in l or 'saint' in l:
        return True
    if 'удалён' in l or 'remote' in l or 'can be' in l:
        return True
    return False

def parse_salary_min(text):
    if not text:
        return 0
    digits = re.findall(r'(\d[\d\s]*)', text.replace('\u202f', ' '))
    nums = []
    for d in digits:
        try:
            nums.append(int(d.replace(' ', '').replace('\u202f', '')))
        except:
            pass
    return min(nums) if nums else 0

def _extract_city_from_slug(slug):
    slug_map = {
        'moscow': 'Москва', 'moskva': 'Москва', 'msk': 'Москва',
        'saint-petersburg': 'Санкт-Петербург', 'spb': 'Санкт-Петербург',
        'sankt-peterburg': 'Санкт-Петербург',
    }
    parts = slug.strip('/').split('/')
    if parts and parts[0] in slug_map:
        return slug_map[parts[0]]
    return ''

# ===== Альфа-Банк (JSON API) =====
def parse_alfa_bank(max_items=300):
    result = []
    seen = set()
    page_size = 100
    MIN_SALARY = 250000

    for skip in range(0, max_items, page_size):
        url = f'https://job.alfabank.ru/api/vacancies?take={page_size}&skip={skip}'
        data = _fetch_json(url)
        if not data:
            break
        items = data.get('items', [])
        if not items:
            break
        for item in items:
            vid = item.get('id', '')
            if not vid or vid in seen:
                continue
            seen.add(vid)

            title = item.get('name', '').strip()
            if not title or any(w in title.lower() for w in EXCLUDE_WORDS):
                continue

            slug = item.get('slug', '')
            city = _extract_city_from_slug(slug)
            if city:
                if not is_moscow_spb(city):
                    continue

            salary = ''
            min_sal = item.get('minSalary')
            if min_sal and min_sal > 0:
                if min_sal < MIN_SALARY:
                    continue
                salary = f'от {min_sal:,} ₽'.replace(',', ' ')

            created = item.get('createdAt', '')[:10]
            pub_date = created if created else ''

            result.append({
                'Id': f'alfa-{vid}',
                'Title': title,
                'Company': 'Альфа-Банк',
                'Salary': salary,
                'Location': city if city else '',
                'PubDate': pub_date,
                'Url': f'https://job.alfabank.ru{slug}' if slug else '',
                'Source': 'Альфа-Банк'
            })
        time.sleep(0.3)
    return result

# ===== Норникель (SSR HTML, пагинация по ?page=N) =====
def parse_nornickel(max_pages=10):
    result = []
    seen = set()
    MIN_SALARY = 250000

    for page in range(1, max_pages + 1):
        url = f'https://career.nornickel.ru/vacancies?page={page}'
        html = _fetch(url)
        if not html:
            break

        # Ищем блоки a.filter-app__result
        blocks = re.findall(
            r'<a\s+class="filter-app__result"[^>]*href="(/vacancy/\d+[^"]*)"[^>]*>(.*?)</a>',
            html, re.DOTALL
        )
        if not blocks:
            break

        found_any = False
        for href, inner in blocks:
            vid_m = re.search(r'/vacancy/(\d+)', href)
            if not vid_m:
                continue
            vid = vid_m.group(1)
            if vid in seen:
                continue
            seen.add(vid)
            found_any = True

            title_m = re.search(r'class="filter-app__result-name"[^>]*>(.*?)</div>', inner, re.DOTALL)
            if not title_m:
                continue
            title = re.sub(r'<[^>]+>', '', title_m.group(1)).strip()
            if not title or any(w in title.lower() for w in EXCLUDE_WORDS):
                continue

            date_m = re.search(r'class="filter-app__result-date"[^>]*>(.*?)</div>', inner, re.DOTALL)
            date = date_m.group(1).strip() if date_m else ''

            salary = ''
            sal_m = re.search(r'class="filter-app__result-salary-from"[^>]*>(.*?)<', inner, re.DOTALL)
            if sal_m:
                sal_raw = sal_m.group(1).strip()
                sal_min = parse_salary_min(sal_raw)
                if sal_min > 0 and sal_min < MIN_SALARY:
                    continue
                salary = sal_raw

            location = ''
            loc_m = re.search(r'class="filter-app__result-location"[^>]*>(.*?)<', inner, re.DOTALL)
            if loc_m:
                location = loc_m.group(1).strip()

            if not is_moscow_spb(location):
                continue

            vurl = f'https://career.nornickel.ru{href}' if href.startswith('/') else href

            result.append({
                'Id': f'nornickel-{vid}',
                'Title': title,
                'Company': 'Норникель',
                'Salary': salary,
                'Location': location,
                'PubDate': date,
                'Url': vurl,
                'Source': 'Норникель'
            })

        if not found_any:
            break
        time.sleep(0.5)

    return result

# ===== Северсталь (SSR HTML, ?page=23 выдаёт все 229) =====
def parse_severstal():
    result = []
    seen = set()

    html = _fetch('https://career.severstal.com/vacancies/?page=23')
    if not html:
        return result

    blocks = re.findall(
        r'card-vacancy__title-text[^>]*>(.*?)</h3>.*?card-vacancy__place[^>]*>(.*?)</div>.*?card-vacancy__date[^>]*>(.*?)</time>',
        html, re.DOTALL
    )

    links = re.findall(r'href="(/vacancies/[^"]+)"[^>]*class="card-vacancy', html)

    for i, (title_raw, place_raw, date_raw) in enumerate(blocks):
        title = re.sub(r'<[^>]+>', '', title_raw).strip()
        place = re.sub(r'<[^>]+>', '', place_raw).strip()
        date = re.sub(r'<[^>]+>', '', date_raw).strip()

        if not title or any(w in title.lower() for w in EXCLUDE_WORDS):
            continue

        location = place.split('(')[0].strip()
        if not is_moscow_spb(location):
            continue

        vurl = f'https://career.severstal.com{links[i]}' if i < len(links) else 'https://career.severstal.com/vacancies'

        key = re.sub(r'[^a-zа-я0-9]', '', (title + location).lower())[:40]
        if key in seen:
            continue
        seen.add(key)

        result.append({
            'Id': f'severstal-{key}',
            'Title': title,
            'Company': 'Северсталь',
            'Salary': '',
            'Location': location,
            'PubDate': date,
            'Url': vurl,
            'Source': 'Северсталь'
        })

    return result
