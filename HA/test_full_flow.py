import paramiko, json, time, urllib.request

TOKEN = 'CHANGE_ME'

def api(path, method="GET", data=None):
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(f"http://192.168.1.92:8123/api/{path}", data=body, headers=headers, method=method)
    try:
        return json.load(urllib.request.urlopen(req, timeout=15))
    except urllib.error.HTTPError as e:
        return {"error": f"{e.code}: {e.read().decode()[:500]}"}

# Find all automation entities
states = api("states")
print("=== All automation entities ===")
eco2_auto = None
for s in states:
    if s["entity_id"].startswith("automation."):
        print(f"  {s['entity_id']} = {s['state']} ({s.get('attributes',{}).get('friendly_name','')})")
        if "eco2" in s["entity_id"].lower() or "mclh" in s["entity_id"].lower():
            eco2_auto = s["entity_id"]

print(f"\n=== Current eCO2 value ===")
for s in states:
    if "eco2" in s["entity_id"].lower():
        print(f"  {s['entity_id']} = {s['state']}")

# Manually trigger the automation to test
if eco2_auto:
    print(f"\n=== Triggering {eco2_auto} manually ===")
    result = api(f"services/automation/trigger", method="POST", data={
        "entity_id": eco2_auto
    })
    print(f"  Result: {json.dumps(result, ensure_ascii=False)[:200]}")
    print("  Wait 5 seconds for TTS to play...")
    time.sleep(5)

# Also test direct TTS on second speaker
print("\n=== Direct TTS test on Station Mini ===")
result2 = api("services/media_player/play_media", method="POST", data={
    "entity_id": "media_player.yandex_station_m10ns3600380kb",
    "media_content_id": "Внимание! Уровень углекислого газа повышен. Рекомендуется включить вентиляцию.",
    "media_content_type": "text"
})
print(f"  TTS result: {json.dumps(result2, ensure_ascii=False)[:200]}")
