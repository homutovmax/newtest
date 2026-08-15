#!/usr/bin/env python3
"""Import vacancies_history.json + cover_v*.html into PostgreSQL."""
import json
import os
import re
import glob
from datetime import datetime

from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session

from src.config import settings
from src.models import Vacancy
from src.classifier import classify_title


def run(dry_run=False):
    base = os.path.dirname(os.path.abspath(__file__))
    history_path = os.path.join(base, "..", "vacancies_history.json")
    covers_glob = os.path.join(base, "..", "cover_v*.html")

    engine = create_engine(settings.db_url)
    Vacancy.metadata.create_all(engine)

    with Session(engine) as session:
        # 1. Load history
        with open(history_path, "r", encoding="utf-8") as f:
            raw = json.load(f)  # flat dict keyed by id

        total = len(raw)
        imported = 0
        skipped = 0
        for vid, item in raw.items():
            title = item.get("title") or ""
            if not title:
                skipped += 1
                continue

            first_seen_str = item.get("firstSeen", "")
            last_seen_str = item.get("lastSeen", "")
            try:
                first_seen = datetime.strptime(first_seen_str, "%Y-%m-%d").date() if first_seen_str else datetime.now().date()
                last_seen = datetime.strptime(last_seen_str, "%Y-%m-%d").date() if last_seen_str else first_seen
            except (ValueError, TypeError):
                first_seen = last_seen = datetime.now().date()

            existing = session.get(Vacancy, vid)
            if existing:
                existing.title = title
                existing.company = item.get("company", "")
                existing.salary = item.get("salary", "")
                existing.location = item.get("location", "")
                existing.url = item.get("url", "")
                existing.source = item.get("source", "hh.ru")
                existing.category = classify_title(title)
                existing.status = item.get("status", "active")
                existing.first_seen = first_seen
                existing.last_seen = last_seen
            else:
                session.add(Vacancy(
                    id=vid,
                    title=title,
                    company=item.get("company", ""),
                    salary=item.get("salary", ""),
                    location=item.get("location", ""),
                    url=item.get("url", ""),
                    source=item.get("source", "hh.ru"),
                    category=classify_title(title),
                    status=item.get("status", "new"),
                    first_seen=first_seen,
                    last_seen=last_seen,
                ))
            imported += 1

        session.commit()
        print(f"История: {imported} импортировано, {skipped} пропущено (из {total})")

        # 2. Import cover_v*.html → extract plain letter text
        cover_files = glob.glob(os.path.join(base, "..", "cover_v*.html"))
        cover_map = {}
        for cf in cover_files:
            m = re.search(r"cover_v(\d+)\.html$", cf)
            if m:
                idx = int(m.group(1))
                with open(cf, "r", encoding="utf-8") as f:
                    html = f.read()
                # Extract .letter-text content from full HTML page
                lm = re.search(r'<div class="letter-text">(.+?)</div>', html, re.DOTALL)
                if lm:
                    text = lm.group(1)
                    text = text.replace('<br>', '\n').replace('<br/>', '\n')
                    text = re.sub(r'</?strong>', '', text)
                    cover_map[idx] = text
                else:
                    cover_map[idx] = re.sub(r'<[^>]+>', '', html)

        updated = 0
        # Match by order (cover_v1 -> first vacancy, etc)
        all_vacancies = session.execute(
            select(Vacancy).order_by(Vacancy.first_seen.desc(), Vacancy.title)
        ).scalars().all()

        for idx, vacancy in enumerate(all_vacancies):
            text = cover_map.get(idx + 1)
            if text and not vacancy.cover_text:
                vacancy.cover_text = text
                updated += 1

        session.commit()
        print(f"Cover-писем импортировано: {updated}")
        print("Миграция завершена.")


if __name__ == "__main__":
    run()
