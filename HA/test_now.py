import paramiko, json, urllib.request

TOKEN = 'CHANGE_ME'

req = urllib.request.Request("http://192.168.1.92:8123/api/services/media_player/play_media",
    data=json.dumps({
        "entity_id": "media_player.yandex_station_r1099440084h0y",
        "media_content_id": "Внимание! Уровень углекислого газа повышен. Рекомендуется включить вентиляцию.",
        "media_content_type": "text"
    }).encode(),
    headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
    method="POST")
urllib.request.urlopen(req, timeout=30)
print("TTS отправлено на Станцию Миди")
