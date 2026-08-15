import paramiko, json, urllib.request

TOKEN = 'CHANGE_ME'

def api(path, method="GET", data=None):
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(f"http://192.168.1.92:8123/api/{path}", data=body, headers=headers, method=method)
    try:
        return json.load(urllib.request.urlopen(req, timeout=30))
    except urllib.error.HTTPError as e:
        return {"error": f"{e.code}: {e.read().decode()[:300]}"}

# Check both speakers status
states = api("states")
for s in states:
    if "yandex_station" in s["entity_id"]:
        print(f"{s['entity_id']}: state={s['state']}, volume={s.get('attributes',{}).get('volume_level','?')}, muted={s.get('attributes',{}).get('is_volume_muted','?')}")

# Try speaker 1
print("\n--- Тест колонки 1 (Модуль/ТВ) ---")
r1 = api("services/media_player/play_media", method="POST", data={
    "entity_id": "media_player.yandex_station_r1099440084h0y",
    "media_content_id": "Тест. Одна.",
    "media_content_type": "text"
})
print(f"  Result: {r1}")

import time
time.sleep(8)

# Try speaker 2 with command type
print("\n--- Тест колонки 2 (Мини) с command ---")
r2 = api("services/media_player/play_media", method="POST", data={
    "entity_id": "media_player.yandex_station_m10ns3600380kb",
    "media_content_id": "Скажи: Внимание, повышен уровень углекислого газа",
    "media_content_type": "command"
})
print(f"  Result: {r2}")

time.sleep(5)

# Try speaker 2 with text type
print("\n--- Тест колонки 2 (Мини) с text ---")
r3 = api("services/media_player/play_media", method="POST", data={
    "entity_id": "media_player.yandex_station_m10ns3600380kb",
    "media_content_id": "Привет! Это тестовое сообщение от Home Assistant.",
    "media_content_type": "text"
})
print(f"  Result: {r3}")

time.sleep(5)

# Try speaker 1 with text
print("\n--- Тест колонки 1 (Модуль/ТВ) с text ---")
r4 = api("services/media_player/play_media", method="POST", data={
    "entity_id": "media_player.yandex_station_r1099440084h0y",
    "media_content_id": "Привет! Это тестовое сообщение от Home Assistant.",
    "media_content_type": "text"
})
print(f"  Result: {r4}")
