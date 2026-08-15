import paramiko, json, urllib.request

TOKEN = 'CHANGE_ME'

def api(path, method="GET", data=None):
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(f"http://192.168.1.92:8123/api/{path}", data=body, headers=headers, method=method)
    try:
        return json.load(urllib.request.urlopen(req, timeout=15))
    except urllib.error.HTTPError as e:
        return {"error": f"{e.code}: {e.read().decode()[:300]}"}

states = api("states")

# Search for yndx
print("=== Все сущности с 'yndx' ===")
for s in states:
    if "yndx" in s["entity_id"].lower() or "yndx" in s.get("attributes",{}).get("friendly_name","").lower():
        print(f"  {s['entity_id']} = {s['state']}")
        for k,v in s.get("attributes",{}).items():
            print(f"    {k}: {v}")

# Search for station
print("\n=== Все media_player ===")
for s in states:
    if "media_player" in s["entity_id"]:
        a = s.get("attributes",{})
        print(f"  {s['entity_id']}")
        print(f"    state: {s['state']}, name: {a.get('friendly_name','')}, model: {a.get('model','')}")

# Device registry
print("\n=== Устройства с yndx ===")
req = urllib.request.Request("http://192.168.1.92:8123/api/config/device_registry/list",
    headers={"Authorization": f"Bearer {TOKEN}"})
devices = json.load(urllib.request.urlopen(req, timeout=15))
for d in devices:
    name = d.get("name","").lower()
    identifiers = str(d.get("identifiers",""))
    if "yndx" in name or "yndx" in identifiers or "yandex" in name or "station" in name:
        print(f"  {d.get('name','')} id={d.get('id','')}")
        print(f"    identifiers: {d.get('identifiers',[])}")
        print(f"    model: {d.get('model','')}, manufacturer: {d.get('manufacturer','')}")
