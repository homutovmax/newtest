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

# Get detailed info about Yandex stations
states = api("states")
for s in states:
    if "yandex_station" in s["entity_id"]:
        print(f"\n=== {s['entity_id']} ===")
        print(f"  State: {s['state']}")
        attrs = s.get("attributes", {})
        for k, v in attrs.items():
            print(f"  {k}: {v}")

# Test TTS on first speaker
print("\n=== Testing TTS on first speaker ===")
result = api("services/media_player/play_media", method="POST", data={
    "entity_id": "media_player.yandex_station_r1099440084h0y",
    "media_content_id": "Тестовое сообщение. Датчик качества воздуха работает.",
    "media_content_type": "text"
})
print(f"  Result: {json.dumps(result, ensure_ascii=False)[:300]}")
