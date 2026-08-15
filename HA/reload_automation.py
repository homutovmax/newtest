import paramiko, json, urllib.request

TOKEN = 'CHANGE_ME'

def api(path, method="GET", data=None):
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(f"http://192.168.1.92:8123/api/{path}", data=body, headers=headers, method=method)
    try:
        return json.load(urllib.request.urlopen(req, timeout=15))
    except urllib.error.HTTPError as e:
        return {"error": f"{e.code}: {e.read().decode()[:500]}"}

# Reload automations
print("=== Reloading automations ===")
result = api("services/automation/reload", method="POST", data={})
print(f"  Result: {json.dumps(result, ensure_ascii=False)[:200]}")

# Check automation state
import time
time.sleep(2)

print("\n=== Checking automation ===")
states = api("states")
for s in states:
    if "mclh" in s["entity_id"].lower() or "eco2" in s["entity_id"].lower():
        print(f"  {s['entity_id']} = {s['state']}")

# Check all automations
print("\n=== All automation entities ===")
for s in states:
    if s["entity_id"].startswith("automation."):
        print(f"  {s['entity_id']} = {s['state']} ({s.get('attributes',{}).get('friendly_name','')})")

# Test TTS manually
print("\n=== Testing TTS on Yandex Station ===")
result2 = api("services/media_player/play_media", method="POST", data={
    "entity_id": "media_player.yandex_station_m10ns3600380kb",
    "media_content_id": "Внимание! Уровень углекислого газа повышен. Рекомендуется включить вентиляцию.",
    "media_content_type": "text"
})
print(f"  TTS sent: {json.dumps(result2, ensure_ascii=False)[:200]}")
