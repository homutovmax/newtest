import sys
sys.path.insert(0, '/opt/hr')
from src.notifications.email import send_digest
send_digest(
    "HR: тестовое письмо",
    "<h2>Рассылка работает</h2><p>Если вы это видите — email настроен верно.</p>",
)
print("Email sent OK")
