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

# Submit QR method
print("=== Selecting QR auth method ===")
result = api(f"config/config_entries/flow/{FLOW_ID}", method="POST", data={
    "method": "qr"
})
print(f"  Type: {result.get('type')}")
print(f"  Step: {result.get('step_id')}")
print(f"  Full: {json.dumps(result, ensure_ascii=False)[:800]}")

if result.get("type") == "external_step":
    url = result.get("url", "")
    print(f"\n  === AUTHORIZATION REQUIRED ===")
    print(f"  Open this URL in browser:")
    print(f"  {url}")
elif result.get("type") == "form":
    schema = result.get("data_schema", [])
    print(f"  Form fields: {[s.get('name') for s in schema]}")
    desc = result.get("description_placeholders", {})
    for k, v in desc.items():
        print(f"  {k}: {v}")
