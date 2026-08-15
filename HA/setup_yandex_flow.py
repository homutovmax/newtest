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

# Step 1: Start flow
print("=== Starting config flow ===")
result = api("config/config_entries/flow", method="POST", data={
    "handler": "yandex_smart_home",
    "show_advanced_options": True
})
flow_id = result.get("flow_id", "")
print(f"  Flow ID: {flow_id}")
print(f"  Step: {result.get('step_id')}")
print(f"  Description: {json.dumps(result.get('description_placeholders',{}), ensure_ascii=False)}")

# Step 2: Submit the user step (empty form)
print("\n=== Submitting user step ===")
result2 = api(f"config/config_entries/flow/{flow_id}", method="POST", data={})
print(f"  Result: {json.dumps(result2, ensure_ascii=False)[:600]}")

# Check if we got an external auth step
if result2.get("type") == "external_step":
    url = result2.get("url", "")
    print(f"\n  === AUTHORIZATION REQUIRED ===")
    print(f"  Open this URL in browser:")
    print(f"  {url}")
    print(f"  After authorizing, the flow will continue automatically")
elif result2.get("type") == "form":
    print(f"\n  Form step: {result2.get('step_id')}")
    print(f"  Schema: {json.dumps(result2.get('data_schema',[]), ensure_ascii=False)[:300]}")
elif result2.get("type") == "create_entry":
    print(f"\n  Created! Entry: {json.dumps(result2.get('result',{}), ensure_ascii=False)[:300]}")
else:
    print(f"\n  Unknown result type: {result2.get('type')}")
