import time
from urllib.parse import quote
from src.scrapers.shared import HH_QUERIES, EXCLUDE_WORDS, fetch, parse_hh_from_search, parse_salary_min, is_moscow_spb, log
from src.classifier import classify_title


def scrape_all():
    results = []
    seen = set()
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
                    for item in items:
                        tid = item['id']
                        key = f'hh-{tid}'
                        if key not in seen:
                            seen.add(key)
                            item['id'] = key
                            item['source'] = 'hh.ru'
                            item['category'] = classify_title(item['title'])
                            item['salary'] = parse_salary_min(item.get('salary', ''))
                            results.append(item)
                time.sleep(0.3)
    log(f'hh.ru: {len(results)} вакансий')
    return results
