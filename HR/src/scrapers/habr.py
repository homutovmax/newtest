from src.scrapers.shared import HABR_QUERIES, EXCLUDE_WORDS, fetch, get_habr_vacancies, log
from src.classifier import classify_title


def scrape_all():
    results = []
    seen = set()
    for label in HABR_QUERIES:
        log(f"Habr: {label}")
        items = get_habr_vacancies(label)
        for item in items:
            tid = item["id"]
            if not tid.startswith("habr-"):
                tid = f"habr-{tid}"
            if tid in seen:
                continue
            seen.add(tid)
            item["id"] = tid
            item["source"] = "Habr Career"
            item["category"] = classify_title(item["title"])
            results.append(item)
        log(f"  +{len(items)} вакансий")
    log(f"Habr: {len(results)} вакансий")
    return results
