#!/usr/bin/env python3
# update_vacancies.py — Ежедневное обновление подборки вакансий (hh.ru + Habr Career) + Telegram

import requests
import re
import json
import html as html_mod
import os
import sys
import time
from datetime import datetime, timedelta
from urllib.parse import quote

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Import classify_title from generate_cover.py (single source of truth)
_COVER_DIR = os.environ.get('HR_HTML_DIR', BASE_DIR)
if _COVER_DIR and os.path.exists(_COVER_DIR):
    sys.path.insert(0, _COVER_DIR)
from generate_cover import classify_title, generate_letter
try:
    from generate_cover_ai import generate_cover as ai_generate_cover
except ImportError:
    ai_generate_cover = None
try:
    from parse_company_portals import parse_alfa_bank, parse_nornickel, parse_severstal
except ImportError:
    parse_alfa_bank = parse_nornickel = parse_severstal = None

# Директория для HTML-файлов (public_html на Beget, текущая для локального теста)
HTML_DIR = os.environ.get('HR_HTML_DIR', BASE_DIR)

REPORT_PATH = os.path.join(HTML_DIR, 'vacancies_report.html')
HISTORY_PATH = os.path.join(BASE_DIR, 'vacancies_history.json')
HISTORY_PAGE_PATH = os.path.join(HTML_DIR, 'vacancies_history.html')
TG_TOKEN = "CHANGE_ME"
TG_CHAT_ID = "777125029"

# Публичный URL (заменить на ваш домен после деплоя)
PUBLIC_URL = os.environ.get('HR_PUBLIC_URL', 'http://maximum64.beget.tech')

MONTHS_RU = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']
HABR_QUERIES = [
    "руководитель направления AI", "Head of AI", "CPO product AI",
    "директор по продукту AI", "цифровая трансформация", "руководитель направления телеком",
    "CTO AI", "руководитель направления стратегия", "директор по трансформации",
    "Head of product AI", "AI архитектор", "технический директор AI",
    # BA profile
    "руководитель бизнес-анализа", "Lead Business Analyst", "бизнес-аналитик",
    "BPMN аналитик", "системный аналитик", "управление требованиями"
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
HH_EMPLOYER_QUERIES = [
    ("Альфа-Банк", 80), ("Сбер", 3529), ("Ростелеком", 2748),
    ("СИБУР", 3809), ("Еврохим", 2501), ("БКС", 1833),
    ("ASTERUS", 3879789), ("Норникель", 740), ("Ivi", 136929),
    ("Северсталь", 6041), ("Газпром нефть", 39305), ("Роснефть", 6596),
    ("Лукойл", 907345), ("Росатом", 577743), ("Ростех", 219911),
    ("РЖД", 23427), ("Россети", 3607), ("РусГидро", 8434),
    ("НЛМК", 988387), ("ФосАгро", 2227671), ("Уралкалий", 38322),
]
EXCLUDE_WORDS = ['продаж', 'sales', 'developer', 'support', 'техподдержк', 'разработчик', 'специалист',                  '1с', 'hr-', 'hr ', 'hr_manager',
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
                 # non-IT industry roles
                 'пищев', 'шоколад', 'морожен', 'кондитер', 'упаковк',
                 'биотехнолог', 'производств', 'фабрик', 'недвижимость',
                 'бренд-шеф', 'категорийн', 'младший', 'ключевых клиентов',
                  'привлечени', 'инвестици', 'брокер',
                  'персональн', 'премьер', 'ассистент', 'помощник', 'личн',
                 # marketing, SMM, content
                 'smm', 'маркетинг', 'продвиж', 'контент-менеджер', 'reels-maker',
                 'маркетплейс', 'ozon', 'wildberries', 'промо', 'промо-менеджер',
                 # interns, juniors, students
                 'стажер', 'стажёр', 'intern', 'trainee', 'студент',
                 # legal, HR, finance, admin
                 'юрисконсульт', 'юридическ', 'правов', 'нормативн', 'комплаенс',
                 'кадров', 'оплат', 'льгот', 'компенсац', 'вознаграждени',
                 'hr ', 'hr_', 'кадр', 'персонал',
                 'финансовым', 'ндфл', 'бухгалтерск', 'управленческ отчетност',
                 'cfo', 'финансов', 'казначейств', 'инкасс',
                 # procurement, logistics
                 'закупк', 'закупок', 'снабжен', 'логистик',
                 # construction, industrial
                 'смет', 'инженер надзора', 'инженер сопровождени',
                 'инженер верифика', 'благоустройств', 'такелаж',
                 'слесарь', 'товаровед', 'мастер участк', 'промышлен',
                 'машиностро', 'машиностроитель', 'металлург', 'горн',
                 # PR, comms, brand
                 'pr менеджер', 'pr-менеджер', 'коммуникац', ' медийн', 'бренд-стратег',
                 # education, methodology
                 'учебн', 'методолог', 'образовательн',
                 # ESG, sustainability
                 'esg', 'устойчив', 'климат', 'углерод',
                 # telecom non-IT
                 'абонент', 'подключени абонент', 'обслуживани абонент',
                 # too vague / non-management
                 'эксперт штаба', 'советник отдела', 'специалист отдела',
                 # security non-IT
                 'чоп', 'физическ', 'охранник', 'секьюрити',
                 # specific non-IT roles
                 'клиентский менеджер по работе с физическими лицами',
                 'клиентский менеджер отделения банка',
                 'менеджер выездного сервиса',
                 'менеджер по крупнейшим клиентам',
                 'менеджер по работе с заказчиками',
                 'промоутер', 'андеррайтер', 'субагент',
                 # more non-IT
                 'game analyst', 'игр', 'гейм',
                 'аналитик соц', 'аналитик кампаний',
                 'web-аналитик', 'веб-аналитик', 'таргетолог',
                 'digital marketing', 'digital-стратег', 'медапланер',
                 ]

session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})

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
    """Keep only Moscow, Saint Petersburg or remote jobs."""
    if not loc:
        return True  # no location info → keep (better than losing relevant)
    l = loc.lower()
    if 'москв' in l or 'москов' in l or 'санкт-петербург' in l or 'saint' in l:
        return True
    if 'удалён' in l or 'remote' in l or 'can be' in l:
        return True
    return False

# ===== Habr Career =====
def get_habr_vacancies(query, pages=3):
    result = []
    seen_ids = set()
    
    for page in range(1, pages + 1):
        url = f'https://career.habr.com/vacancies?q={quote(query)}&type=all&page={page}'
        html_text = fetch(url, 'https://career.habr.com/')
        if not html_text:
            continue
        
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
            
            pub_date = ''
            m = re.search(r'basic-date[^>]+>([^<]+)<', block)
            if m:
                pub_date = m.group(1).strip()
            
            if len(title) > 100 or not title:
                continue
            
            is_irr = any(w in title.lower() for w in EXCLUDE_WORDS)
            if is_irr:
                continue

            # Habr-specific: only keep management/leadership roles
            # Reject individual contributor roles (developer, QA, DevOps, SRE, DBA)
            tl = title.lower()
            
            # Strong management/leadership keywords — these alone are enough
            strong_mgmt = [
                'руководител', 'директор', 'head of', 'head ', 'начальник',
                'team lead', 'tech lead', 'тимлид',
                'cto', 'cio', 'cdo', 'cpo',
                'управляющ', 'управлен',
            ]
            # Strategy / transformation / architecture / product keywords
            strat_mgmt = [
                'стратег', 'трансформац', 'цифров',
                'архитектор', 'методолог',
                'продукт', 'product owner', 'product manager',
            ]
            # Tech leadership keywords (senior enough to be relevant)
            tech_lead = [
                'lead', 'лид ',
                'data ', 'ml ', 'ai ', 'ии ',
                'нейросет', 'машинн',
                'platform', 'платформ',
            ]
            # Words that indicate individual contributor (reject if present WITHOUT strong mgmt)
            dev_words = [
                'разработчик', 'developer', 'backend', 'frontend', 'fullstack', 'full-stack',
                'engineer', 'инженер', 'qa', 'тестировщик', 'dba', 'devops', 'sre',
                'android', 'ios', 'mobile', 'react', 'node',
                'python', 'java', 'golang', 'scala', 'kotlin',
                'data engineer', 'data scientist', 'ml engineer',
                'вертика', 'вертик', 'средн', 'middle', 'junior', 'senior',
                'системный аналитик', 'продуктовый аналитик', 'аналитик данных',
                'data analyst', 'bi аналитик', 'bi-аналитик',
                'fullstack', 'automation qa', 'manual qa',
            ]
            has_strong = any(w in tl for w in strong_mgmt)
            has_strat = any(w in tl for w in strat_mgmt)
            has_tech = any(w in tl for w in tech_lead)
            has_dev = any(w in tl for w in dev_words)
            
            # Exception: "бизнес-аналитик" is relevant (management)
            has_ba = 'бизнес' in tl and 'аналитик' in tl
            
            # Keep if has strong mgmt or strat keywords
            if has_strong or has_strat:
                pass  # keep
            elif has_ba:
                pass  # keep бизнес-аналитик
            elif has_tech and not has_dev:
                pass  # keep tech lead without dev words
            elif has_dev:
                continue  # reject individual contributor
            else:
                continue  # reject if no relevant keywords
            
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
                if min_sal > 0 and min_sal < 250000:
                    continue
            
            result.append({
                'Id': f'habr-{vid}', 'Title': title, 'Company': company,
                'Salary': salary, 'Location': location, 'PubDate': pub_date,
                'Url': vurl, 'Source': 'Habr Career'
            })
    
    return result

# ===== Telegram =====
def send_telegram(message):
    try:
        body = {
            'chat_id': TG_CHAT_ID, 'text': message,
            'parse_mode': 'HTML', 'disable_web_page_preview': True
        }
        r = requests.post(f'https://api.telegram.org/bot{TG_TOKEN}/sendMessage',
                          json=body, timeout=15)
        r.raise_for_status()
        log('Telegram: отправлено')
    except Exception as e:
        log(f'Telegram: ошибка {e}')

# ===== MAIN =====
log('=== ОБНОВЛЕНИЕ ПОДБОРКИ ВАКАНСИЙ ===')
today_str = format_date_ru()
log(f'Дата: {today_str}')
today_iso = datetime.now().strftime('%Y-%m-%d')

all_vacancies = []
seen_keys = set()

# -- hh.ru --
def parse_salary_min(sal_text):
    """Extract minimum monthly salary in RUB from text like 'от 125 000 ₽' or '125 000 – 150 000 ₽'. Returns 0 if unknown."""
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
            # strip dummy (100 ₽, 100 руб., etc.)
            c = re.sub(r'[\s\u00a0\u20bd\u0440\u0443\u0431\.]', '', sal_raw)
            if c not in ('', '100', '0', '–'):
                salary = re.sub(r',?\s*за\s+\w+.*', '', sal_raw)
                salary = re.sub(r',?\s*до\s+вычета.*', '', salary)
                salary = salary.strip()
        
        location = ''
        lm = re.search(r'data-qa="vacancy-serp__vacancy-address"[^>]*>([^<]+)', block)
        if lm:
            location = lm.group(1).strip()
        if not is_moscow_spb(location):
            continue
        
        date = ''
        dm = re.search(r'magritte-text_style-tertiary[^>]*>.*?<span>([^<]+)</span>', block)
        if dm:
            date = dm.group(1).strip()
        
        # Skip if salary is visible and below minimum
        if salary:
            sal_min = parse_salary_min(salary)
            if sal_min > 0 and sal_min < MIN_SALARY:
                continue
        
        items.append({
            'Id': vid, 'Title': title, 'Company': company,
            'Salary': salary, 'Location': location, 'PubDate': date,
            'Url': f'https://hh.ru/vacancy/{vid}',
            'Source': 'hh.ru'
        })
    return items

PAGES = 5
for name, query in HH_QUERIES:
    for mode in ['name_only', 'full_text']:
        sf = '&search_field=name' if mode == 'name_only' else ''
        for page in range(PAGES):
            url = f'https://hh.ru/search/vacancy?text={quote(query)}&area=113&order_by=publication_time&items_on_page=20&page={page}{sf}'
            log(f'hh.ru: {name} [{mode}] p{page}...')
            html_text = fetch(url)
            if html_text:
                items = parse_hh_from_search(html_text)
                for it in items:
                    key = f'hh-{it["Id"]}'
                    if key not in seen_keys:
                        all_vacancies.append(it)
                        seen_keys.add(key)
            time.sleep(0.3)

# -- hh.ru employer search --
def is_employer_relevant(title):
    """For employer queries, only keep IT/management roles (not all roles from the company)."""
    t = title.lower()
    
    # Reject: non-IT, individual contributor, junior roles
    reject_words = [
        'sap ', 'sap/', '1с', 'программист', 'смет', 'проектиров',
        'слесарь', 'электрик', 'сантехник', 'водитель', 'охранник',
        'юрист', 'бухгалтер', 'экономист', 'кадр', 'hr ',
        'маркетолог', 'pr ', 'реклам', 'сmm',
        'стажер', 'стажёр', 'intern', 'junior', 'младший',
        'промоутер', 'продавец', 'кассир', 'курьер',
        'товаровед', 'кладовщик', 'грузчик',
    ]
    if any(w in t for w in reject_words):
        return False
    
    # Must contain at least one strong management keyword
    strong_mgmt = [
        'руководител', 'директор', 'head of', 'head ', 'начальник',
        'team lead', 'tech lead', 'тимлид',
        'cto', 'cio', 'cdo', 'cpo',
        'управляющ', 'управлен',
    ]
    strat_mgmt = [
        'стратег', 'трансформац', 'цифров',
        'архитектор', 'методолог',
        'продукт', 'product owner', 'product manager',
    ]
    tech_lead = [
        'lead', 'лид ',
        'data ', 'ml ', 'ai ', 'ии ',
        'нейросет', 'машинн',
        'platform', 'платформ',
    ]
    dev_words = [
        'разработчик', 'developer', 'engineer', 'инженер',
        'backend', 'frontend', 'fullstack', 'full-stack',
        'qa', 'тестировщик', 'dba', 'devops', 'sre',
    ]
    
    has_strong = any(w in t for w in strong_mgmt)
    has_strat = any(w in t for w in strat_mgmt)
    has_tech = any(w in t for w in tech_lead)
    has_dev = any(w in t for w in dev_words)
    has_ba = 'бизнес' in t and 'аналитик' in t
    
    if has_strong or has_strat or has_ba:
        return True
    if has_tech and not has_dev:
        return True
    return False

for name, eid in HH_EMPLOYER_QUERIES:
    log(f'hh.ru employer: {name} (id={eid})...')
    url = f'https://hh.ru/search/vacancy?employer_id={eid}&area=113&order_by=publication_time&items_on_page=20'
    html_text = fetch(url)
    if html_text:
        items = parse_hh_from_search(html_text)
        for it in items:
            key = f'hh-{it["Id"]}'
            if key not in seen_keys:
                # For employer queries, only keep IT/management roles
                if not is_employer_relevant(it.get('Title', '')):
                    continue
                it['Company'] = name
                it['company_vacancy'] = True
                all_vacancies.append(it)
                seen_keys.add(key)
    time.sleep(0.3)

# -- Company career portals --
portal_parsers = [
    ('Альфа-Банк', parse_alfa_bank, {'max_items': 300}),
    ('Норникель', parse_nornickel, {'max_pages': 10}),
    ('Северсталь', parse_severstal, {}),
]
portal_count = 0
for pname, pfunc, pkwargs in portal_parsers:
    if not pfunc:
        continue
    log(f'Career portal: {pname}...')
    try:
        items = pfunc(**pkwargs)
        for it in items:
            key = it['Id']
            if key not in seen_keys:
                it['company_vacancy'] = True
                all_vacancies.append(it)
                seen_keys.add(key)
                portal_count += 1
        log(f'  +{len(items)} вакансий')
    except Exception as e:
        log(f'  Ошибка: {e}')
    time.sleep(0.3)

hh_count = sum(1 for v in all_vacancies if v['Source'] == 'hh.ru')
empl_count = sum(1 for v in all_vacancies if v.get('company_vacancy'))
log(f'hh.ru: {hh_count} вакансий (из них {empl_count} от целевых компаний, включая карьерные порталы: {portal_count})')

# -- Habr Career --
for query in HABR_QUERIES:
    log(f'Habr: {query}...')
    vac_list = get_habr_vacancies(query)
    for v in vac_list:
        key = v['Id']
        if key not in seen_keys:
            all_vacancies.append(v)
            seen_keys.add(key)
    log(f'  +{len(vac_list)} вакансий')
    time.sleep(0.5)

hh_count = sum(1 for v in all_vacancies if v['Source'] == 'hh.ru')
# -- rabota.sber.ru --
SBER_MGMT = [
    'руководител', 'директор', 'head of', 'head', 'начальник',
    'team lead', 'tech lead', 'тимлид',
    'cto', 'cio', 'cdo', 'cpo',
    'управляющ', 'управлен',
    'стратег', 'трансформац', 'цифров',
    'архитектор', 'методолог',
    'продукт', 'product owner', 'product manager',
    'lead', 'лид ',
    'data ', 'ml ', 'ai ', 'ии ',
    'нейросет', 'машинн',
    'platform', 'платформ',
]
SBER_REJECT = [
    'клиентский менеджер', 'менеджер по закупкам', 'юрисконсульт',
    'бренд-стратег', 'pr менеджер', 'pr-менеджер',
    'архитектор благоустройства', 'стажер', 'стажёр', 'студент',
    'менеджер выездного сервиса', 'менеджер по работе с клиентами',
    'инженер по смет', 'смет', 'инженер верифика', 'инженер надзора',
     'казначейств', 'инкасс', 'кредитн', ' рисков',
    'менеджер по крупнейшим клиентам', 'менеджер отделения банка',
    'менеджер по работе с заказчиками', 'аналитик в ценообразован',
    'менеджер по работе с физическими лицами', 'менеджер по продвиж',
    'субагент', 'таргетолог', ' game analyst', 'игр',
    'менеджер Центра популяризац', 'менеджер по AI-аналитике',
    'эксперт штаба блока', 'советник управления',
    'старший бренд', 'эксперт по управлению качеством',
    'инженер-верификатор', 'специалист по оценке рисков',
    'solution-инженер', 'solution инженер',
    'программист 1с',
    'менеджер по продажам', 'менеджер по продаж',
    'менеджер по коммуникац', 'менеджер по связям',
    'менеджер по безопасности', 'менеджер по регуляторике',
    'менеджер по compliance', 'менеджер по аудиту',
    ' qa', 'qa-', 'devops', 'sre', 'dba',
    'разработчик', 'developer', 'backend', 'frontend', 'fullstack',
    'data scientist', 'ml инженер', 'data инженер', 'data engineer',
    'middle ', 'junior ', 'senior ',
    'аналитик (junior)', 'бизнес-аналитик (junior)',
]

def parse_sber_vacancies():
    result = []
    seen_ids = set()
    skip = 0
    take = 50
    max_vacancies = 500
    SBER_API = 'https://rabota.sber.ru/public/app-candidate-public-api-gateway/api/v1/publications'
    t_start = time.time()

    while skip < max_vacancies:
        url = f'{SBER_API}?skip={skip}&take={take}'
        data = None
        for attempt in range(3):
            try:
                t0 = time.time()
                r = session.get(url, timeout=30)
                r.raise_for_status()
                data = r.json()
                log(f'  sber page skip={skip} — {len(data.get("data",{}).get("vacancies",[]))} vac, {time.time()-t0:.1f}s')
                break
            except Exception as e:
                if attempt < 2:
                    time.sleep(1 * (attempt + 1))
                else:
                    log(f'  rabota.sber.ru: ошибка {e} (3 попытки)')

        if data is None:
            break

        vacancies = data.get('data', {}).get('vacancies', [])
        total = data.get('data', {}).get('total', 0)

        if not vacancies:
            break

        for v in vacancies:
            vid = v.get('publicationId', '')
            if not vid or vid in seen_ids:
                continue
            seen_ids.add(vid)

            title = v.get('title', '')
            if not title or any(w in title.lower() for w in EXCLUDE_WORDS):
                continue

            tl = title.lower()
            has_mgmt = any(w in tl for w in SBER_MGMT)
            has_reject = any(w in tl for w in SBER_REJECT)
            if has_reject or not has_mgmt:
                continue

            company = v.get('company', 'Сбер')

            salary = ''
            salary_min = v.get('salary_min')
            salary_max = v.get('salary_max')
            if salary_min and salary_max:
                salary = f'{salary_min} – {salary_max} ₽'
            elif salary_min:
                salary = f'от {salary_min} ₽'
            elif salary_max:
                salary = f'до {salary_max} ₽'
            c = re.sub(r'[\s\u00a0\u20bd\u0440\u0443\u0431\.]', '', salary)
            if c in ('', '100', '0', '–'):
                salary = ''

            location = v.get('city', '')
            if not is_moscow_spb(location):
                region = v.get('region', '')
                if not is_moscow_spb(region):
                    continue

            pub_date = v.get('publicationDate', '')[:10]

            internal_id = v.get('internalId', '')

            result.append({
                'Id': vid,
                'Title': title,
                'Company': company,
                'Salary': salary,
                'Location': location,
                'PubDate': pub_date,
                'Url': f'https://rabota.sber.ru/search/{internal_id}/',
                'Source': 'Сбер (rabota.sber.ru)'
            })

        skip += take
        if skip >= total:
            break

    log(f'  sber: итого {len(result)} вакансий за {time.time()-t_start:.1f}s')
    return result

sber_count = 0
log('rabota.sber.ru: загрузка вакансий...')
sber_vacancies = parse_sber_vacancies()
for v in sber_vacancies:
    key = f'sber-{v["Id"]}'
    if key not in seen_keys:
        all_vacancies.append(v)
        seen_keys.add(key)
        sber_count += 1
log(f'  +{sber_count} вакансий')

hh_count = sum(1 for v in all_vacancies if v['Source'] == 'hh.ru')
habr_count = sum(1 for v in all_vacancies if v['Source'] == 'Habr Career')
log(f'Всего вакансий: {len(all_vacancies)}')

# ===== HISTORY =====
history = {}
if os.path.exists(HISTORY_PATH):
    try:
        with open(HISTORY_PATH, 'r', encoding='utf-8-sig') as f:
            raw = json.load(f)
        if isinstance(raw, list):
            for item in raw:
                k = item.get('key', item['id'] if item.get('source') == 'Habr Career' else f'sber-{item["id"]}' if item.get('source') == 'Сбер (rabota.sber.ru)' else f'hh-{item["id"]}')
                history[k] = item
        else:
            history = raw
    except Exception as e:
        log(f'Ошибка загрузки истории: {e}')

active_keys = set()
def vacancy_key(v):
    if v['Source'] == 'hh.ru':
        return f'hh-{v["Id"]}'
    elif v['Source'] == 'Сбер (rabota.sber.ru)':
        return f'sber-{v["Id"]}'
    else:
        return v['Id']

for v in all_vacancies:
    key = vacancy_key(v)
    active_keys.add(key)
    if key in history:
        history[key]['lastSeen'] = today_iso
        if history[key].get('firstSeen') != today_iso:
            history[key]['status'] = 'active'
        history[key]['title'] = v['Title']
        history[key]['company'] = v['Company']
        history[key]['salary'] = v['Salary']
        history[key]['location'] = v['Location']
    else:
        history[key] = {
            'key': key, 'id': v['Id'], 'source': v['Source'],
            'title': v['Title'], 'company': v['Company'],
            'salary': v['Salary'], 'location': v['Location'],
            'url': v['Url'],
            'firstSeen': today_iso, 'lastSeen': today_iso,
            'status': 'new'
        }

closed_today = []
for key in list(history.keys()):
    if key not in active_keys and history[key].get('status') != 'closed':
        history[key]['status'] = 'closed'
        history[key]['lastSeen'] = today_iso
        closed_today.append(history[key])

with open(HISTORY_PATH, 'w', encoding='utf-8') as f:
    json.dump(history, f, ensure_ascii=False, indent=2)
log(f'История сохранена: {len(history)} записей')

new_today = [v for v in history.values() if v.get('status') == 'new' and v.get('firstSeen') == today_iso]
active_now = [v for v in history.values() if v.get('status') in ('active', 'new')]
closed_only = [v for v in history.values() if v.get('status') == 'closed']

# Sort: new today first, then with salary first
new_keys = set()
for v in new_today:
    key = v.get('key', '')
    if not key:
        if v.get('source') == 'hh.ru':
            key = f'hh-{v.get("id", "")}'
        elif v.get('source') == 'Сбер (rabota.sber.ru)':
            key = f'sber-{v.get("id", "")}'
        else:
            key = v.get('id', '')
    if key:
        new_keys.add(key)
all_vacancies.sort(key=lambda v: (
    0 if v.get('company_vacancy') else 1,
    0 if vacancy_key(v) in new_keys else 1,
    0 if v['Salary'] else 1
))

# Classify each vacancy into a scenario
for v in all_vacancies:
    v['Scenario'] = classify_title(v.get('Title', ''))

# ===== GENERATE HISTORY HTML =====
def gen_hist_html():
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
    <div class="stat-card new"><div class="num">{len(new_today)}</div><div class="label">Новых сегодня</div></div>
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
    
    # New today
    lines.append(f'<div class="section-title">🆕 Новые сегодня <span class="badge">{len(new_today)}</span></div>')
    if not new_today:
        lines.append('<p style="color: var(--muted); font-size: 14px;">Новых вакансий сегодня нет</p>')
    else:
        for v in sorted(new_today, key=lambda x: (x.get('source', ''), x.get('title', ''))):
            lines.append(vac_card(v, 'new', 'NEW'))
    
    # Active
    active_list = [v for v in active_now if v.get('status') == 'active']
    lines.append(f'<div class="section-title">✅ Активные <span class="badge">{len(active_list)}</span></div>')
    if not active_list:
        lines.append('<p style="color: var(--muted); font-size: 14px;">Нет активных вакансий</p>')
    else:
        for v in sorted(active_list, key=lambda x: (x.get('source', ''), x.get('title', ''))):
            lines.append(vac_card(v, 'active', 'активна'))
    
    # Closed today
    lines.append(f'<div class="section-title">❌ Закрыто сегодня <span class="badge">{len(closed_today)}</span></div>')
    if not closed_today:
        lines.append('<p style="color: var(--muted); font-size: 14px;">Закрытых сегодня нет</p>')
    else:
        for v in sorted(closed_today, key=lambda x: (x.get('source', ''), x.get('title', ''))):
            lines.append(vac_card(v, 'closed', 'закрыта'))
    
    # Older closed
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

hist_html = gen_hist_html()
with open(HISTORY_PAGE_PATH, 'w', encoding='utf-8') as f:
    f.write(hist_html)
log(f'История сохранена: {HISTORY_PAGE_PATH}')

# ===== GENERATE MAIN REPORT HTML =====
def gen_report_html():
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
  <div class="date">Обновлено {today_str} · Москва · hh.ru + Habr Career + Сбер + Карьерные порталы</div>
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
    <div class="stat-card portal"><div class="num">{portal_count}</div><div class="label">Карьерные порталы</div></div>
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
    
    # Build vacancy card for each tab
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
                th = esc(v['Title'])
                tc = esc(v['Company'])
                tl = esc(v['Location'])
                ts = esc(v['Salary'])
                tp = esc(v.get('PubDate', ''))
                
                salary_display = ts
                salary_tag = f'<span class="meta-tag salary">{salary_display}</span>' if salary_display else ''
                date_tag = f'<span class="meta-tag">{tp}</span>' if v.get('PubDate') else ''
                loc_tag = f'<span class="meta-tag">{tl}</span>'
                if v['Source'] == 'Habr Career':
                    src_class = 'habr'
                    btn_label = 'Открыть на Habr'
                    site_id = v['Id'].replace('habr-', '')
                elif v['Source'] == 'Сбер (rabota.sber.ru)':
                    src_class = 'sber'
                    btn_label = 'Открыть на rabota.sber.ru'
                    site_id = v['Id']
                else:
                    src_class = 'hh'
                    btn_label = 'Открыть на hh.ru'
                    site_id = v['Id']
                src_tag = f'<span class="meta-tag {src_class}">{v["Source"]}</span>'
                company_display = tc if tc else v['Source']
                salary_attr = ts
                lines.append(f'''  <div class="vacancy" data-vacancy-id="v{idx}" data-site="{v['Source']}" data-site-id="{site_id}" data-title="{th}" data-company="{company_display}" data-salary="{salary_attr}" data-location="{tl}" data-url="{esc(v['Url'])}">
    <div class="vacancy-header">
      <div>
        <a class="vacancy-title" href="{v['Url']}" target="_blank">{th}</a>
        <div class="vacancy-company">{company_display}</div>
      </div>
      <span class="status-badge">актуально</span>
    </div>
    <div class="vacancy-meta">
      {loc_tag} {salary_tag} {date_tag} {src_tag}
    </div>
    <div class="vacancy-actions">
      <a class="btn btn-primary" href="{v['Url']}" target="_blank">{btn_label}</a>
      <button class="btn btn-cover" onclick="openCover('v{idx}')">Сопроводительное</button>
      <button class="btn btn-resume" onclick="openResume('v{idx}')">Резюме</button>
      <button class="btn btn-telegram" onclick="sendToTelegram('v{idx}')">📲 Telegram</button>
    </div>
  </div>''')
        lines.append('</div>')
    
    lines.append(f'''  <div class="empty-note">
    <strong>Карьерные порталы целевых компаний:</strong><br>
    <a href="https://hh.ru/employer/4234" target="_blank">МТС</a> ·
    <a href="https://www.company.rt.ru/career/vacancy/" target="_blank">Ростелеком</a> ·
    <a href="https://hh.ru/employer/4243" target="_blank">T2 (Tele2)</a> ·
    <a href="https://rabota.sber.ru" target="_blank">Сбер</a> ·
    <a href="https://job.alfabank.ru" target="_blank">Альфа-Банк</a> ·
    <a href="https://tbank.ru/career" target="_blank">Т-Банк</a> ·
    <a href="https://sibur.ru/career" target="_blank">СИБУР</a> ·
    <a href="https://eurochem.ru/career" target="_blank">Еврохим</a>
  </div>
  <div class="last-updated">
    Последнее обновление: {today_str} · Следующее: {(datetime.now() if datetime.now().hour < 14 else datetime.now() + timedelta(days=1)).strftime("%d.%m.%Y")} в 10:00 и 14:00
  </div>
</div>
<div class="toast" id="toast"></div>
<script>
function showToast(msg) {{
  var t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(function() {{ t.classList.remove('show'); }}, 5000);
}}
function switchTab(tabId) {{
  document.querySelectorAll('.tab-content').forEach(function(el) {{ el.style.display = 'none'; }});
  document.querySelectorAll('.tab-btn').forEach(function(el) {{ el.classList.remove('active'); }});
  document.getElementById('tab-' + tabId).style.display = 'block';
  document.querySelector('.tab-btn[data-tab="' + tabId + '"]').classList.add('active');
}}
function openCover(id) {{
  window.open('cover_' + id + '.html', '_blank');
}}
function openResume(id) {{
  var el = document.querySelector('[data-vacancy-id="' + id + '"]');
  if (!el) return;
  var title = encodeURIComponent(el.dataset.title || (el.querySelector('.vacancy-title')?.textContent?.trim()) || id);
  var company = encodeURIComponent(el.dataset.company || (el.querySelector('.vacancy-company')?.textContent?.trim()) || '');
  var site = encodeURIComponent(el.dataset.site || '');
  var siteId = encodeURIComponent(el.dataset.siteId || '');
  var salary = encodeURIComponent(el.dataset.salary || '');
  var location = encodeURIComponent(el.dataset.location || '');
  var url = encodeURIComponent(el.dataset.url || el.querySelector('.vacancy-title')?.href || '');
  window.open('resume.php?title=' + title + '&company=' + company + '&site=' + site + '&id=' + siteId + '&url=' + url + '&salary=' + salary + '&location=' + location, '_blank');
}}
function sendToTelegram(id) {{
  var el = document.querySelector('[data-vacancy-id="' + id + '"]');
  if (!el) return;
  var params = 'title=' + encodeURIComponent(el.dataset.title || '') +
    '&company=' + encodeURIComponent(el.dataset.company || '') +
    '&site=' + encodeURIComponent(el.dataset.site || '') +
    '&id=' + encodeURIComponent(el.dataset.siteId || '') +
    '&salary=' + encodeURIComponent(el.dataset.salary || '') +
    '&location=' + encodeURIComponent(el.dataset.location || '') +
    '&url=' + encodeURIComponent(el.dataset.url || '') +
    '&type=both';
  var btn = event.target;
  btn.textContent = '⏳ Отправка...';
  btn.disabled = true;
  fetch('send_to_telegram.php?' + params)
    .then(r => r.text())
    .then(t => {{ btn.textContent = t.includes('Sent') ? '✅ Отправлено' : '❌ Ошибка'; setTimeout(function() {{ btn.textContent = '📲 Telegram'; btn.disabled = false; }}, 3000); }})
    .catch(function() {{ btn.textContent = '❌ Ошибка'; setTimeout(function() {{ btn.textContent = '📲 Telegram'; btn.disabled = false; }}, 3000); }});
}}
</script>
</body>
</html>''')
    
    return '\n'.join(lines)

report_html = gen_report_html()
with open(REPORT_PATH, 'w', encoding='utf-8') as f:
    f.write(report_html)
log(f'Отчёт сохранён: {REPORT_PATH}')

# ===== GENERATE COVER LETTERS =====
cover_generated = 0
cover_ai = 0

def _cover_html(ct, cc, cl, cs, letter_text, category):
    ct_e = html_mod.escape(ct)
    cc_e = html_mod.escape(cc)
    cl_e = html_mod.escape(cl) if cl else ''
    cs_e = html_mod.escape(cs) if cs else ''
    # convert **bold** to <strong>bold</strong>
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

for i, v in enumerate(all_vacancies, 1):
    idx = f'v{i}'
    ct = html_mod.unescape(v['Title'])
    cc = html_mod.unescape(v.get('Company', ''))
    cs = html_mod.unescape(v.get('Salary', ''))
    cl = html_mod.unescape(v.get('Location', ''))
    is_ai = False
    letter_text = ''
    category = ''
    try:
        if ai_generate_cover:
            letter_text, category = ai_generate_cover(ct, cc, 0, cs, cl)
            if letter_text:
                is_ai = True
    except Exception:
        pass
    if not letter_text:
        try:
            letter_text, category = generate_letter(ct, cc, 0, cs, cl)
        except Exception:
            pass
    if not letter_text:
        continue
    cover_html = _cover_html(ct, cc, cl, cs, letter_text, category)
    cover_path = os.path.join(HTML_DIR, f'cover_{idx}.html')
    with open(cover_path, 'w', encoding='utf-8') as cf:
        cf.write(cover_html)
    cover_generated += 1
    if is_ai:
        cover_ai += 1
log(f'Сгенерировано обложек: {cover_generated}/{len(all_vacancies)} (AI: {cover_ai})')

# ===== SEND TELEGRAM =====
new_today_telegram = []
for v in all_vacancies:
    key = vacancy_key(v)
    if key in new_keys:
        new_today_telegram.append(v)

emoji = ['1️⃣','2️⃣','3️⃣','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣','9️⃣','🔟']
msg_lines = [f'<b>📊 Новые вакансии • {today_str}</b>',
             f'hh.ru: {hh_count} · Habr Career: {habr_count} · Сбер: {sber_count} · Всего: {len(all_vacancies)}',
             f'<b>Новых сегодня: {len(new_today_telegram)}</b>',
             '']
for i, v in enumerate(new_today_telegram[:10]):
    n = emoji[i] if i < len(emoji) else f'{i+1}.'
    src = '🔵 Habr' if v['Source'] == 'Habr Career' else '🔴 hh'
    sal = f' · {esc(v["Salary"])}' if v['Salary'] else ''
    loc = f' · {esc(v.get("Location", ""))}' if v.get('Location') else ''
    msg_lines.append(f'{n} <a href="{v["Url"]}">{esc(v["Title"])}</a>')
    msg_lines.append(f'   {src} · {esc(v["Company"])}{sal}{loc}')

msg_lines.append('')
if len(new_today_telegram) > 10:
    msg_lines.append(f'... и ещё {len(new_today_telegram) - 10} вакансий')
msg_lines.append(f'Подробнее: {PUBLIC_URL}/vacancies_report.html')

send_telegram('\n'.join(msg_lines))
# Аналитика после генерации отчёта
try:
    import subprocess
    r = subprocess.run([sys.executable, os.path.join(BASE_DIR, 'run_analytics.py')],
                       cwd=BASE_DIR, capture_output=True, text=True, timeout=30)
    for line in r.stdout.strip().split('\n'):
        log(line)
    if r.returncode != 0:
        log(f'АНАЛИТИКА: отчёт об ошибках: {PUBLIC_URL}/vacancies_analytics.html')
except Exception as exc:
    log(f'АНАЛИТИКА: ошибка {exc}')
log('=== ГОТОВО ===')
