import time, re
from src.scrapers.shared import fetch, EXCLUDE_WORDS, is_moscow_spb, log
from src.classifier import classify_title

SBER_API = 'https://rabota.sber.ru/public/app-candidate-public-api-gateway/api/v1/publications'

SBER_MGMT = [
    'руководител', 'директор', 'head of', 'head ', 'начальник',
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
    ' казначейств', 'инкасс', 'кредитн', ' рисков',
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


def _clean_salary(salary_str):
    c = re.sub(r'[\s\u00a0\u20bd\u0440\u0443\u0431\.]', '', salary_str)
    if c in ('', '100', '0', '–'):
        return ''
    return salary_str


def scrape_all():
    result = []
    seen_ids = set()
    skip = 0
    take = 50
    max_vacancies = 500
    t_start = time.time()

    while skip < max_vacancies:
        url = f'{SBER_API}?skip={skip}&take={take}'
        data = None
        for attempt in range(3):
            try:
                t0 = time.time()
                r_text = fetch(url)
                if r_text is None:
                    continue
                import json
                data = json.loads(r_text)
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
            salary = _clean_salary(salary)

            location = v.get('city', '')
            if not is_moscow_spb(location):
                region = v.get('region', '')
                if not is_moscow_spb(region):
                    continue

            internal_id = v.get('internalId', '')

            key = f'sber-{vid}'
            result.append({
                'id': key,
                'title': title,
                'company': company,
                'salary': salary,
                'location': location,
                'url': f'https://rabota.sber.ru/search/{internal_id}/',
                'source': 'Сбер (rabota.sber.ru)',
                'category': classify_title(title),
            })

        skip += take
        if skip >= total:
            break

    log(f'  sber: итого {len(result)} вакансий за {time.time()-t_start:.1f}s')
    return result
