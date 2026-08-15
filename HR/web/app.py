import html
import re
from fastapi import FastAPI, Request, Depends, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from datetime import date

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from src.database import get_session
from src.models import Vacancy, PipelineRun
from src.classifier import classify_title
from src.cover import generate_letter
from src.pipeline_monitor import get_recent_runs, get_last_run, get_stats

SCENARIO_LABELS = {1: "Telecom / IT", 2: "AI / Product", 3: "Strategic", 4: "Business Analysis"}


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response


app = FastAPI(title="HR Vacancy Dashboard", docs_url=None, redoc_url=None, openapi_url=None)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[
        "ibox-z3-2.taila7bc1e.ts.net",
        "192.168.1.92",
        "localhost",
        "127.0.0.1",
    ],
)
templates = Jinja2Templates(directory="web/templates")
app.mount("/static", StaticFiles(directory="web/static"), name="static")


def scenario_label(cat: str) -> str:
    return {
        "telecom": "Telecom / IT",
        "ai_product": "AI / Product",
        "strategy": "Strategic",
        "ba": "Business Analysis",
        "unknown": "Other",
    }.get(cat, "Other")


@app.get("/", response_class=HTMLResponse)
async def index():
    return RedirectResponse(url="/report")


@app.get("/report", response_class=HTMLResponse)
async def report(
    request: Request,
    tab: str = Query(default="all"),
    db: Session = Depends(get_session),
):
    stmt = select(Vacancy).order_by(
        Vacancy.status.desc(),
        Vacancy.last_seen.desc(),
    )
    vacancies = db.execute(stmt).scalars().all()

    today = date.today()
    total = len(vacancies)
    new_today = sum(1 for v in vacancies if v.first_seen == today)
    hh_count = sum(1 for v in vacancies if v.source == "hh.ru")
    habr_count = sum(1 for v in vacancies if v.source == "Habr Career")

    if tab != "all":
        category_map = {"telecom": "telecom", "ai": "ai_product", "strategy": "strategy", "ba": "ba", "other": "unknown"}
        cat = category_map.get(tab)
        if tab == "other":
            vacancies = [v for v in vacancies if v.category in (None, "unknown")]
        elif cat:
            vacancies = [v for v in vacancies if v.category == cat]

    return templates.TemplateResponse(request, "report.html", {
        "vacancies": vacancies,
        "total": total,
        "new_today": new_today,
        "hh_count": hh_count,
        "habr_count": habr_count,
        "active_tab": tab,
        "scenario_label": scenario_label,
        "today": today,
    })


@app.get("/resume", response_class=HTMLResponse)
async def resume(
    request: Request,
    title: str = Query(default=""),
    company: str = Query(default=""),
    scenario: int = Query(default=0),
    db: Session = Depends(get_session),
):
    if not title:
        return HTMLResponse("Укажите title в query-параметрах", status_code=400)
    cat = classify_title(title)
    scenario_map = {"telecom": 1, "ai_product": 2, "strategy": 3, "ba": 4, "unknown": 1}
    if scenario == 0:
        scenario = scenario_map.get(cat, 1)

    return templates.TemplateResponse(request, "resume.html", {
        "title": title,
        "company": company,
        "scenario": scenario,
        "cat": cat,
        "cat_label": SCENARIO_LABELS.get(scenario, scenario_label(cat)),
    })


@app.get("/cover/{vid}", response_class=HTMLResponse)
async def cover(
    request: Request,
    vid: str,
    db: Session = Depends(get_session),
):
    vacancy = db.get(Vacancy, vid)
    if not vacancy:
        return HTMLResponse("Вакансия не найдена", status_code=404)

    if not vacancy.cover_text:
        text, cat = generate_letter(vacancy.title, vacancy.company or "")
        cover_text = text
    else:
        cover_text = vacancy.cover_text
        # Detect full HTML page stored by migration — extract .letter-text content
        if cover_text.lstrip().startswith('<!DOCTYPE') or cover_text.lstrip().startswith('<html'):
            m = re.search(r'<div class="letter-text">(.+?)</div>', cover_text, re.DOTALL)
            if m:
                cover_text = m.group(1)
                cover_text = cover_text.replace('<br>', '\n').replace('<br/>', '\n')
                cover_text = re.sub(r'</?strong>', '', cover_text)

    cover_text = html.escape(cover_text)
    cover_text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', cover_text)
    cover_text = cover_text.replace('\n', '<br>')

    return templates.TemplateResponse(request, "cover.html", {
        "vacancy": vacancy,
        "cover_text": cover_text,
    })


@app.get("/analytics", response_class=HTMLResponse)
async def analytics(
    request: Request,
    db: Session = Depends(get_session),
):
    total = db.execute(select(func.count(Vacancy.id))).scalar() or 0

    by_category = dict(
        db.execute(
            select(Vacancy.category, func.count(Vacancy.id))
            .group_by(Vacancy.category)
        ).all()
    )

    by_source = dict(
        db.execute(
            select(Vacancy.source, func.count(Vacancy.id))
            .group_by(Vacancy.source)
        ).all()
    )

    by_status = dict(
        db.execute(
            select(Vacancy.status, func.count(Vacancy.id))
            .group_by(Vacancy.status)
        ).all()
    )

    today = date.today()
    new_today = db.execute(
        select(func.count(Vacancy.id)).where(Vacancy.first_seen == today)
    ).scalar() or 0

    # Issues
    no_salary = db.execute(
        select(func.count(Vacancy.id)).where(
            Vacancy.salary.is_(None) | (Vacancy.salary == "")
        )
    ).scalar() or 0

    long_company = db.execute(
        select(Vacancy.id, Vacancy.title, Vacancy.company)
        .where(func.length(Vacancy.company) > 200)
        .limit(10)
    ).all()

    no_category = by_category.get(None, 0)

    return templates.TemplateResponse(request, "analytics.html", {
        "total": total,
        "by_category": {k: v for k, v in by_category.items() if k is not None},
        "uncategorized": no_category,
        "by_source": by_source,
        "by_status": by_status,
        "new_today": new_today,
        "no_salary": no_salary,
        "long_company": long_company,
    })


@app.get("/history", response_class=HTMLResponse)
async def history(
    request: Request,
    db: Session = Depends(get_session),
):
    vacancies = db.execute(
        select(Vacancy).order_by(Vacancy.last_seen.desc())
    ).scalars().all()
    return templates.TemplateResponse(request, "history.html", {
        "vacancies": vacancies,
        "scenario_label": scenario_label,
    })


@app.get("/monitoring", response_class=HTMLResponse)
async def monitoring(request: Request):
    runs = get_recent_runs(30)
    last_run = get_last_run()
    stats = get_stats()
    return templates.TemplateResponse(request, "monitoring.html", {
        "runs": runs,
        "last_run": last_run,
        "stats": stats,
    })


@app.get("/health")
async def health():
    last_run = get_last_run()
    return {
        "status": "ok",
        "last_pipeline": {
            "id": last_run.id if last_run else None,
            "status": last_run.status if last_run else None,
            "started_at": last_run.started_at.isoformat() if last_run else None,
            "total_vacancies": last_run.total_vacancies if last_run else None,
            "duration_seconds": last_run.duration_seconds if last_run else None,
        } if last_run else None,
    }
