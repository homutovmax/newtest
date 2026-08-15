import sys, os, json, re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from generate_cover import classify_title
from src.scrapers.shared import log

HISTORY_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "vacancies_history.json")
REPORT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "vacancies_report.html")


def check():
    issues = []
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # 1. Exclude words
    exclude_check = ["персональн", "премьер", "ассистент", "помощник", "личн"]
    report_path = os.path.join(base, REPORT_PATH)
    if os.path.exists(report_path):
        with open(report_path, "r", encoding="utf-8") as f:
            html = f.read()
        found = [w for w in exclude_check if w.lower() in html.lower()]
        if found:
            issues.append({
                "msg": f"Найдены exclude-слова: {', '.join(found)}",
                "fix": "Добавить в EXCLUDE_WORDS в src/scrapers/shared.py",
            })

    # 2. Dummy salaries
    dummy = re.findall(r"(?<!\d)100\s*[₽р]", html) if os.path.exists(report_path) else []
    if dummy:
        issues.append({
            "msg": f"Найдено {len(dummy)} dummy-зарплат",
            "fix": "Проверить parse_salary_min()",
        })

    # 3. Double prefix
    hist_path = os.path.join(base, HISTORY_PATH)
    if os.path.exists(hist_path):
        with open(hist_path, "r", encoding="utf-8") as f:
            hist = json.load(f)
        double = [k for k in hist if "habr-habr" in k]
        if double:
            issues.append({
                "msg": f"Найдено {len(double)} double-prefix",
                "fix": "Очистить vacancies_history.json",
            })

    # 4. Classification smoke test
    smoke = [
        ("Системный аналитик", "ba"),
        ("Head of AI", "ai_product"),
        ("Директор по цифровой трансформации", "strategy"),
        ("CTO телеком", "telecom"),
        ("Продавец", "unknown"),
    ]
    for title, expected in smoke:
        result = classify_title(title)
        if result != expected:
            issues.append({
                "msg": f"classify_title({title!r}) = {result}, ожидался {expected}",
                "fix": "Проверить ключевые слова в classify_title() generate_cover.py",
            })

    return issues
