import paramiko, json, urllib.request

TOKEN = 'CHANGE_ME'

def api(path):
    req = urllib.request.Request(f"http://192.168.1.92:8123/api/{path}",
        headers={"Authorization": f"Bearer {TOKEN}"})
    return json.load(urllib.request.urlopen(req, timeout=15))

# All entities
states = api("states")

# Look for anything yandex/yadio/station/alice
keywords = ["yandex", "yadio", "station", "alice", "marusya", "sber"]
print("=== Entities matching Yandex/speaker keywords ===")
for s in states:
    eid = s["entity_id"].lower()
    if any(k in eid for k in keywords):
        print(f"  {s['entity_id']} = {s['state']}")

# All media_player
print("\n=== All media_player entities ===")
for s in states:
    if "media_player" in s["entity_id"]:
        attrs = s.get("attributes", {})
        print(f"  {s['entity_id']}")
        print(f"    state: {s['state']}")
        print(f"    friendly_name: {attrs.get('friendly_name','')}")
        print(f"    source: {attrs.get('source','')}")
        print(f"    model: {attrs.get('model','')}")
        print()

# Config entries - look for anything yandex/media related
entries = api("config/config_entries/entry")
print("=== Config entries (non-default) ===")
for e in entries:
    domain = e.get("domain","")
    if domain not in ("homeassistant","http","mobile_app","mqtt","zha","sonos","zeroconf","dhcp","usb","homeworks","map"):
        print(f"  {domain}: {e.get('title','')} (state={e.get('state','')})")

# Check if yandex_smart_home has any device/entity registry entries
print("\n=== Device registry (yandex) ===")
devices = api("config/device_registry/list")
for d in devices:
    if "yandex" in d.get("identifiers", [[]])[0] if d.get("identifiers") else "":
        print(f"  {d.get('name','')} ({d.get('id','')})")

# Check entity registry for yandex
print("\n=== Entity registry (yandex) ===")
ents = api("config/entity_registry/list")
for e in ents:
    if "yandex" in e.get("entity_id","").lower():
        print(f"  {e['entity_id']} (disabled={e.get('disabled_by','')})")
