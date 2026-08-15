import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from deepseek_api import ask
from generate_cover import classify_title

COVER_SYSTEM = (
    'Ты — профессиональный карьерный консультант с 15-летним опытом. '
    'Пишешь сопроводительные письма от имени кандидата. '
    'Письмо должно быть деловым, уверенным, без лести и общих фраз. '
    'Подбери 2-3 самых релевантных факта из опыта под конкретную вакансию. '
    'Не упоминай зарплату. '
    'Язык: русский.'
)

COVER_PROMPT_TPL = (
    'Напиши сопроводительное письмо от имени Максима Хомутова.\n\n'
    'Вакансия: {title}\nКомпания: {company}\n'
    'Локация: {location}\n\n'
    'О кандидате:\n'
    '- 46 лет, 24 года в ИТ и телекоме\n'
    '- Живёт в г. Королёв (МО), готов к командировкам, не готов к переезду\n'
    '- МТС (2021-2026): руководитель направления трайба CX и технологической стратегии\n'
    '  — GenAI-суфлер (голос), NLP (орфография, tone of voice)\n'
    '  — Платформа роботизации КЦ\n'
    '  — Конвейер AI-инициатив 100+/неделю\n'
    '  — Технологическая стратегия кластера: техзрелость до 4/5\n'
    '- Ростелеком (2020-2021): оптимизация кабельных столов, BPMN (Camunda)\n'
    '- СИБУР (2018-2020): создание БА с нуля (11 чел.), change management, управление требованиями\n'
    '- МГТС (2013-2018): управление требованиями GPON, B2B/B2C, программа лояльности\n\n'
    'Ключевые компетенции:\n'
    '— AI/ML: GenAI, NLP, роботизация, R&D-конвейер\n'
    '— Business Analysis: BPMN, UML, EPC, Camunda, управление требованиями\n'
    '— Strategy: технологическая стратегия, цифровая трансформация, change management\n'
    '— Управление: распределённые команды до 50+ чел., бюджет 500 млн+\n\n'
    'Формат письма:\n'
    '1. Приветствие\n'
    '2. Представление (кто вы, почему пишете)\n'
    '3. Опыт (2-3 факта, релевантных вакансии, с цифрами)\n'
    '4. Заключение (готовность к собеседованию)\n'
    '5. Подпись: Максим Хомутов, maxim.khomutov@gmail.com, +7 (916) 192-88-47\n\n'
    'Не добавляй дату, не упоминай зарплату. Только текст письма.'
)

def generate_cover(title, company, scenario=0, salary='', location=''):
    cat = classify_title(title)
    if scenario == 1:
        cat = 'telecom'
    elif scenario == 2:
        cat = 'ai_product'
    elif scenario == 3:
        cat = 'strategy'
    elif scenario == 4:
        cat = 'ba'
    loc = f' ({location})' if location else ''
    prompt = COVER_PROMPT_TPL.format(title=title, company=company, location=loc)
    text = ask(prompt, system=COVER_SYSTEM, max_tokens=1024, temperature=0.7)
    return text, cat

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(json.dumps({'error': 'Usage: generate_cover_ai.py <title_b64> <company_b64> [scenario] [salary_b64] [location_b64]'}))
        sys.exit(1)
    import base64
    title = base64.b64decode(sys.argv[1]).decode('utf-8') if sys.argv[1] else ''
    raw_c = base64.b64decode(sys.argv[2]).decode('utf-8') if sys.argv[2] else ''
    company = '' if raw_c == '_unknown' else raw_c
    scenario = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3].isdigit() else 0
    salary = base64.b64decode(sys.argv[4]).decode('utf-8') if len(sys.argv) > 4 and sys.argv[4] and sys.argv[4] != 'Xw' else ''
    location = base64.b64decode(sys.argv[5]).decode('utf-8') if len(sys.argv) > 5 and sys.argv[5] and sys.argv[5] != 'Xw' else ''
    try:
        text, cat = generate_cover(title, company, scenario, salary, location)
        print(json.dumps({'text': text, 'category': cat}, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({'error': str(e)}, ensure_ascii=False))
        sys.exit(1)
