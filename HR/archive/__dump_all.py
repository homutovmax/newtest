import sys, json
sys.path.insert(0, "/app")
from src.database import SessionLocal
from src.models import Vacancy
from collections import defaultdict

s = SessionLocal()
v = s.query(Vacancy).order_by(Vacancy.category).all()
s.close()

by_cat = defaultdict(list)
for vacancy in v:
    cat = vacancy.category or "unknown"
    by_cat[cat].append(vacancy.title)

# Output as JSON for local analysis
output = {cat: titles for cat, titles in sorted(by_cat.items(), key=lambda x: -len(x[1]))}
print(json.dumps(output, ensure_ascii=False, indent=2))
