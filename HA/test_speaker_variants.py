import paramiko, json, time, urllib.request

TOKEN = 'CHANGE_ME'

def api(path, method="GET", data=None):
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(f"http://192.168.1.92:8123/api/{path}", data=body, headers=headers, method=method)
    try:
        return json.load(urllib.request.urlopen(req, timeout=30))
    except urllib.error.HTTPError as e:
        return {"error": f"{e.code}: {e.read().decode()[:300]}"}

# Check current state
states = api("states")
for s in states:
    if "yandex_station" in s["entity_id"]:
        a = s.get("attributes", {})
        print(f"{s['entity_id']}:")
        print(f"  state: {s['state']}")
        print(f"  volume: {a.get('volume_level','?')}")
        print(f"  muted: {a.get('is_volume_muted','?')}")
        print(f"  alice_state: {a.get('alice_state','?')}")
        print(f"  features: {a.get('supported_features','?')}")
        print()

# Try 1: command type on Mini
print("=== 1. Command on Mini ===")
r = api("services/media_player/play_media", method="POST", data={
    "entity_id": "media_player.yandex_station_m10ns3600380kb",
    "media_content_id": "Привет",
    "media_content_type": "command"
})
print(f"  {r}")
time.sleep(10)

# Try 2: text type on Mini with short text
print("\n=== 2. Text on Mini (short) ===")
r = api("services/media_player/play_media", method="POST", data={
    "entity_id": "media_player.yandex_station_m10ns3600380kb",
    "media_content_id": "Тест",
    "media_content_type": "text"
})
print(f"  {r}")
time.sleep(10)

# Try 3: dialog type on Mini
print("\n=== 3. Dialog on Mini ===")
r = api("services/media_player/play_media", method="POST", data={
    "entity_id": "media_player.yandex_station_m10ns3600380kb",
    "media_content_id": "Внимание, повышен углекислый газ",
    "media_content_type": "dialog"
})
print(f"  {r}")
time.sleep(10)

# Try 4: turn on first, then TTS
print("\n=== 4. Turn on Mini, then text ===")
r = api("services/media_player/turn_on", method="POST", data={
    "entity_id": "media_player.yandex_station_m10ns3600380kb"
})
print(f"  Turn on: {r}")
time.sleep(3)
r = api("services/media_player/play_media", method="POST", data={
    "entity_id": "media_player.yandex_station_m10ns3600380kb",
    "media_content_id": "Внимание! Уровень углекислого газа повышен. Рекомендуется включить вентиляцию.",
    "media_content_type": "text"
})
print(f"  Text: {r}")
