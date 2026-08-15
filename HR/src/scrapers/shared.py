import re
import html as html_mod
import requests
from urllib.parse import quote
from datetime import datetime

session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})

MONTHS_RU = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']

HABR_QUERIES = [
    "руководитель направления AI", "Head of AI", "CPO product AI",
    "директор по продукту AI", "цифровая трансформация", "руководитель направления телеком",
    "CTO AI", "руководитель направления стратегия", "директор по трансформации",
    "Head of product AI", "AI архитектор", "технический директор AI",
    "руководитель бизнес-анализа", "Lead Business Analyst", "бизнес-аналитик",
    "BPMN аналитик", "системный аналитик", "управление требованиями",
]

HH_QUERIES = [
    ("Telecom/IT",
     'руководитель направления OR "Head of" OR "клиентский сервис" OR "delivery manager" OR "руководитель платформы" OR CTO OR DevOps OR телеком OR инфраструктура'),
    ("AI/Product",
     '"Head of AI" OR CPO OR "директор по продукту" OR "AI архитектор" OR "Data Science" OR "руководитель AI" OR "machine learning" OR "искусственный интеллект" OR "R&D" OR "AI продукт"'),
    ("Strategy",
     '"цифровая трансформация" OR стратегия OR "operational excellence" OR "change management" OR "технологическая стратегия" OR эффективность OR трансформация OR инновации OR "организационная эффективность" OR "технологическая зрелость"'),
    ("BA",
     'бизнес-аналитик OR "системный аналитик" OR "business analyst" OR BPMN OR "управление требованиями" OR "руководитель аналитики" OR "Lead BA" OR "аналитик требований" OR "методолог"'),
]

EXCLUDE_WORDS = ['продаж', 'sales', 'developer', 'support', 'техподдержк', 'разработчик', 'специалист', '1С', 'hr-', 'hr ', 'hr_manager',
                 'консультант', 'оператор', 'водитель', 'продавец', 'фармацевт', 'администратор',
                 'официант', 'курьер', 'доставк', 'уборщик', 'мерчендайзер',
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
                 'персональн', 'премьер', 'ассистент', 'помощник', 'личн']


def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    line = f'[{ts}] {msg}'
    print(line, flush=True)


def fetch(url, referer=None):
    hdrs = {}
    if referer:
        hdrs['Referer'] = referer
    try:
        r = session.get(url, headers=hdrs, timeout=30)
        r.raise_for_status()
        return r.text
    except Exception as e:
        log(f'  Ошибка: {e}')
    return None


def esc(s):
    return html_mod.escape(str(s)) if s is not None else ''


def format_date_ru(dt=None):
    if dt is None:
        dt = datetime.now()
    return f'{dt.day} {MONTHS_RU[dt.month-1]} {dt.year}'


def is_moscow_spb(loc):
    if not loc:
        return True
    l = loc.lower()
    if 'москв' in l or 'москов' in l or 'санкт-петербург' in l or 'saint' in l:
        return True
    if 'удалён' in l or 'remote' in l or 'can be' in l:
        return True
    return False


def parse_salary_min(sal_text):
    if not sal_text:
        return 0
    digits = re.findall(r'(\d[\d\s]*)', sal_text.replace('\u202f', ' '))
    nums = []
    for d in digits:
        try:
            nums.append(int(d.replace(' ', '').replace('\u202f', '')))
        except:
            pass
    return min(nums) if nums else 0


def parse_hh_from_search(html_text):
    items = []
    MIN_SALARY = 200000
    for m in re.finditer(r'<div id="(\d+)"[^>]*class="[^"]*vacancy-card[^"]*"[^>]*>(.*?)</div>\s*</div>\s*</div>\s*</div>\s*</div>\s*</div>', html_text, re.DOTALL):
        vid = m.group(1)
        block = m.group(2)

        title = ''
        tm = re.search(r'data-qa="serp-item__title-text"[^>]*>([^<]+)', block)
        if tm:
            title = tm.group(1).strip()
        if not title or any(w in title.lower() for w in EXCLUDE_WORDS):
            continue

        company = ''
        cm = re.search(r'data-qa="vacancy-serp__vacancy-employer-text"[^>]*>([^<]+)', block)
        if cm:
            company = cm.group(1).strip()

        salary = ''
        sm = re.search(r'typography-label-1-regular[^>]*>(.*?)</span>', block, re.DOTALL)
        if sm:
            sal_raw = sm.group(1)
            sal_raw = re.sub(r'<!--.*?-->', '', sal_raw)
            sal_raw = re.sub(r'<[^>]+>', '', sal_raw).strip()
            c = re.sub(r'[\s\u00a0\u20bd\u0440\u0443\u0431\.]', '', sal_raw)
            if c not in ('', '100', '0', '\u2013'):
                salary = re.sub(r',?\s*за\s+\w+.*', '', sal_raw)
                salary = re.sub(r',?\s*до\s+вычета.*', '', salary)
                salary = salary.strip()

        location = ''
        lm = re.search(r'data-qa="vacancy-serp__vacancy-address"[^>]*>([^<]+)', block)
        if lm:
            location = lm.group(1).strip()
        if not is_moscow_spb(location):
            continue

        # Skip if salary is visible and below minimum
        if salary:
            sal_min = parse_salary_min(salary)
            if sal_min > 0 and sal_min < MIN_SALARY:
                continue

        items.append({
            'id': vid, 'title': title, 'company': company,
            'salary': salary, 'location': location,
            'url': f'https://hh.ru/vacancy/{vid}',
            'source': 'hh.ru',
        })
    return items


def get_habr_vacancies(query):
    url = f'https://career.habr.com/vacancies?q={quote(query)}&type=all'
    html_text = fetch(url, 'https://career.habr.com/')
    if not html_text:
        return []

    result = []
    seen_ids = set()
    blocks = html_text.split('<div class="vacancy-card">')

    for block in blocks[1:]:
        m = re.search(r'/vacancies/(\d+)', block)
        if not m:
            continue
        vid = m.group(1)
        if vid in seen_ids:
            continue
        seen_ids.add(vid)
        vurl = f'https://career.habr.com/vacancies/{vid}'

        title = ''
        m = re.search(r'vacancy-card__title-link[^>]*>([^<]+)<', block)
        if m:
            title = m.group(1).strip()

        company = ''
        m = re.search(r'vacancy-card__company[^>]*>.*?link-comp[^>]*>([^<]+)<', block)
        if m:
            company = m.group(1).strip()

        salary = ''
        m = re.search(r'basic-salary[^>]*>([^<]+)<', block)
        if m:
            salary = m.group(1).strip()

        location = ''
        loc_matches = re.findall(r'chip-with-icon__text[^>]*>([^<]+)<', block)
        if len(loc_matches) >= 2:
            location = loc_matches[1].strip()
        elif loc_matches:
            location = loc_matches[0].strip()
        if not is_moscow_spb(location):
            continue

        if len(title) > 100 or not title:
            continue

        is_excluded = any(w in title.lower() for w in EXCLUDE_WORDS)
        if is_excluded:
            continue

        if salary:
            digits = re.findall(r'\d[\d\s]*', salary)
            min_sal = 0
            for d in digits:
                num_str = d.replace(' ', '')
                try:
                    val = int(num_str)
                    if min_sal == 0 or val < min_sal:
                        min_sal = val
                except ValueError:
                    pass
            if min_sal > 0 and min_sal < 400000:
                continue

        result.append({
            'id': f'habr-{vid}', 'title': title, 'company': company,
            'salary': salary, 'location': location,
            'url': vurl, 'source': 'Habr Career',
        })

    return result
