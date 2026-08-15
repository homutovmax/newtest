#!/usr/bin/env python3
"""Orchestrator — runs the full pipeline with monitoring."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scrapers.shared import log
from src.scrapers import hh_ru, habr, sber
from src.pipeline_monitor import start_run, finish_run
from src.config import settings


def run():
    run_id = start_run()
    log(f"=== HR PIPELINE (run #{run_id}) ===")

    hh_count = 0
    habr_count = 0
    sber_count = 0
    total = 0
    new_today = 0

    try:
        # 1. Scrape
        log("--- scraping hh.ru ---")
        hh_vacancies = hh_ru.scrape_all()

        log("--- scraping Habr ---")
        habr_vacancies = habr.scrape_all()

        log("--- scraping Сбер ---")
        sber_vacancies = sber.scrape_all()

        all_vacancies = hh_vacancies + habr_vacancies + sber_vacancies
        hh_count = len(hh_vacancies)
        habr_count = len(habr_vacancies)
        sber_count = len(sber_vacancies)
        total = len(all_vacancies)
        new_today = sum(1 for v in all_vacancies if v.get("status") == "new")
        log(f"Всего найдено: {total}")

        # 2. Merge into history
        from src.merge_history import merge
        merge(all_vacancies)
        log("История обновлена")

        # 3. Generate covers
        from src.generate_covers import generate
        generate(all_vacancies)
        log("Cover-письма сгенерированы")

        # 4. Generate report
        from src.report import generate as gen_report
        gen_report()

        # 5. Analytics
        from src.analytics import check as check_analytics
        issues = check_analytics()
        if issues:
            for iss in issues:
                log(f"АНАЛИТИКА: {iss['msg']} — {iss['fix']}")
        else:
            log("АНАЛИТИКА: все проверки пройдены")

        # 6. Email notification
        from src.notifications.email import send_digest
        public_url = settings.public_url.rstrip('/')
        send_digest(
            f"HR: {new_today} новых вакансий",
            f"<h2>Новые вакансии: {new_today}</h2>"
            f"<p>Всего: {total}</p>"
            f"<p>hh.ru: {hh_count} · Habr: {habr_count} · Сбер: {sber_count}</p>"
            f"<p><a href='{public_url}/report'>Открыть отчёт</a></p>",
        )

        finish_run(run_id, "success", hh_count=hh_count, habr_count=habr_count,
                   total_vacancies=total, new_today=new_today, email_sent=True)
        log("=== HR PIPELINE DONE ===")

    except Exception as e:
        log(f"PIPELINE ERROR: {e}")
        import traceback
        traceback.print_exc()
        finish_run(run_id, "failed", hh_count=hh_count, habr_count=habr_count,
                   total_vacancies=total, new_today=new_today, email_sent=False,
                   error_message=str(e))
        log("=== HR PIPELINE FAILED ===")
        raise


if __name__ == "__main__":
    run()
