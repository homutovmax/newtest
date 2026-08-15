"""Send report email (no re-scrape) — called by cron at 14:00 MSK."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.database import SessionLocal
from src.models import Vacancy
from src.notifications.email import send_digest
from src.config import settings

session = SessionLocal()
total = session.query(Vacancy).count()
new_today = session.query(Vacancy).filter(Vacancy.status == 'new').count()
session.close()

public_url = settings.public_url.rstrip('/')
tailscale_url = "https://ibox-z3-2.taila7bc1e.ts.net"

send_digest(
    f'HR Daily: {new_today} новых, всего {total}',
    f'<h2>HR Daily Digest (14:00)</h2>'
    f'<p>Новых сегодня: <strong>{new_today}</strong></p>'
    f'<p>Всего в базе: {total}</p>'
    f'<p><a href="{public_url}/report">Открыть отчёт</a></p>'
    f'<p><a href="{tailscale_url}/report">Через Tailscale</a></p>',
)
print('Report sent')
