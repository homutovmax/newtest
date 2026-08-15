import paramiko, json, time, urllib.request

HOST = '192.168.1.92'
USER = 'root'
PASS = 'CHANGE_ME'
TOKEN = 'CHANGE_ME'

def api(path, method="GET", data=None):
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(f"http://192.168.1.92:8123/api/{path}", data=body, headers=headers, method=method)
    try:
        return json.load(urllib.request.urlopen(req, timeout=15))
    except urllib.error.HTTPError as e:
        return {"error": f"{e.code}: {e.read().decode()[:500]}"}

# 1. Check config entries
entries = api("config/config_entries/entry")
yash = [e for e in entries if e.get("domain") == "yandex_smart_home"]
print("=== Yandex Smart Home entries ===")
for e in yash:
    print(f"  Title: {e.get('title')}")
    print(f"  State: {e.get('state')}")
    data = e.get("data", {})
    print(f"  Connection: {data.get('connection_type')}")
    print(f"  Data keys: {list(data.keys())}")

# 2. Check all states for new yandex entities
states = api("states")
yandex_entities = [s for s in states if "yandex" in s["entity_id"].lower() or "yaha" in s["entity_id"].lower()]
print(f"\n=== Yandex entities ({len(yandex_entities)}) ===")
for s in yandex_entities:
    print(f"  {s['entity_id']} = {s['state']} ({s.get('attributes',{}).get('friendly_name','')})")

# 3. Check all media_player entities (Yandex speakers show as media_player)
mp = [s for s in states if "media_player" in s["entity_id"]]
print(f"\n=== Media players ({len(mp)}) ===")
for s in mp:
    print(f"  {s['entity_id']} = {s['state']} ({s.get('attributes',{}).get('friendly_name','')})")

# 4. Check for new services
services = api("services")
yandex_svcs = [s for s in services if "yandex" in s["domain"].lower() or "yaha" in s["domain"].lower()]
print(f"\n=== Yandex services ({len(yandex_svcs)}) ===")
for s in yandex_svcs:
    for k, v in s["services"].items():
        print(f"  {s['domain']}.{k}: {v.get('name','')}")
