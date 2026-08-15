import paramiko, json, time, urllib.request

TOKEN = 'CHANGE_ME'
FLOW_ID = "01KW3WBYYMFJNYQDFWBYMVRJMT"

def api(path, method="GET", data=None):
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(f"http://192.168.1.92:8123/api/{path}", data=body, headers=headers, method=method)
    try:
        return json.load(urllib.request.urlopen(req, timeout=15))
    except urllib.error.HTTPError as e:
        return {"error": f"{e.code}: {e.read().decode()[:500]}"}

# Check flow status
print("=== Checking config flow ===")
result = api(f"config/config_entries/flow/{FLOW_ID}")
print(f"  Type: {result.get('type')}")
print(f"  Step: {result.get('step_id')}")
print(f"  Result: {json.dumps(result, ensure_ascii=False)[:800]}")

# Try to submit if still waiting
if result.get("step_id") == "qr":
    print("\n=== Submitting after QR auth ===")
    result2 = api(f"config/config_entries/flow/{FLOW_ID}", method="POST", data={})
    print(f"  Type: {result2.get('type')}")
    print(f"  Step: {result2.get('step_id')}")
    print(f"  Result: {json.dumps(result2, ensure_ascii=False)[:800]}")

# Check config entries
print("\n=== Yandex Station entries ===")
entries = api("config/config_entries/entry")
for e in entries:
    if "yandex" in e.get("domain",""):
        print(f"  {e['domain']}: {e.get('title','')} (state={e.get('state','')})")
        print(f"  Data: {json.dumps(e.get('data',{}), ensure_ascii=False)[:300]}")

# Check for yandex station entities
print("\n=== Yandex entities ===")
states = api("states")
for s in states:
    eid = s["entity_id"].lower()
    if "yandex" in eid or "station" in eid or "alice" in eid:
        print(f"  {s['entity_id']} = {s['state']}")
