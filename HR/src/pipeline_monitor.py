"""Pipeline run tracking — log runs to PostgreSQL and report status."""
from datetime import datetime
from sqlalchemy import select, func, desc
from src.database import SessionLocal
from src.models import PipelineRun


def start_run():
    session = SessionLocal()
    try:
        run = PipelineRun(
            started_at=datetime.now(),
            status="running",
        )
        session.add(run)
        session.commit()
        run_id = run.id
    finally:
        session.close()
    return run_id


def finish_run(run_id: int, status: str, hh_count=0, habr_count=0, total_vacancies=0, new_today=0, email_sent=False, error_message=None):
    session = SessionLocal()
    try:
        run = session.get(PipelineRun, run_id)
        if run:
            now = datetime.now()
            run.finished_at = now
            run.status = status
            run.hh_count = hh_count
            run.habr_count = habr_count
            run.total_vacancies = total_vacancies
            run.new_today = new_today
            run.email_sent = email_sent
            run.error_message = error_message
            run.duration_seconds = int((now - run.started_at).total_seconds())
            session.commit()
    finally:
        session.close()


def get_recent_runs(limit=30):
    session = SessionLocal()
    try:
        runs = session.execute(
            select(PipelineRun).order_by(desc(PipelineRun.started_at)).limit(limit)
        ).scalars().all()
        return runs
    finally:
        session.close()


def get_last_run():
    session = SessionLocal()
    try:
        run = session.execute(
            select(PipelineRun).order_by(desc(PipelineRun.started_at)).limit(1)
        ).scalar_one_or_none()
        return run
    finally:
        session.close()


def get_stats():
    session = SessionLocal()
    try:
        total_runs = session.execute(select(func.count(PipelineRun.id))).scalar() or 0
        success_runs = session.execute(
            select(func.count(PipelineRun.id)).where(PipelineRun.status == "success")
        ).scalar() or 0
        failed_runs = session.execute(
            select(func.count(PipelineRun.id)).where(PipelineRun.status == "failed")
        ).scalar() or 0
        return {
            "total_runs": total_runs,
            "success_runs": success_runs,
            "failed_runs": failed_runs,
            "success_rate": round(success_runs / total_runs * 100, 1) if total_runs > 0 else 0,
        }
    finally:
        session.close()
