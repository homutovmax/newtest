import paramiko, json, urllib.request

TOKEN = 'CHANGE_ME'

def api(path, method="GET", data=None):
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(f"http://192.168.1.92:8123/api/{path}", data=body, headers=headers, method=method)
    try:
        return json.load(urllib.request.urlopen(req, timeout=60))
    except urllib.error.HTTPError as e:
        return {"error": f"{e.code}: {e.read().decode()[:300]}"}

# Direct TTS test on Station Mini
print("=== TTS on Station Mini ===")
result = api("services/media_player/play_media", method="POST", data={
    "entity_id": "media_player.yandex_station_m10ns3600380kb",
    "media_content_id": "Внимание! Уровень углекислого газа повышен. Рекомендуется включить вентиляцию.",
    "media_content_type": "text"
})
print(f"  Result: {result}")
print("\nDid you hear the voice message?")
