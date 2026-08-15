import sys, urllib.request, urllib.parse, json
token = "CHANGE_ME"
chat = "777125029"
msg = sys.stdin.read()
data = urllib.parse.urlencode({"chat_id": chat, "text": msg, "parse_mode": "Markdown"}).encode()
r = urllib.request.urlopen(f"https://api.telegram.org/bot{token}/sendMessage", data)
print(json.loads(r.read())["ok"])
