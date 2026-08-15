import paramiko, json, time, urllib.request

HOST = '192.168.1.92'
USER = 'root'
PASS = 'CHANGE_ME'
TOKEN = 'CHANGE_ME'

FLOW_ID = "01KW3TFHMZYS866V67ZTQRWQ11"

def api(path, method="GET", data=None):
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(f"http://192.168.1.92:8123/api/{path}", data=body, headers=headers, method=method)
    try:
        return json.load(urllib.request.urlopen(req, timeout=15))
    except urllib.error.HTTPError as e:
        return {"error": f"{e.code}: {e.read().decode()[:500]}"}

# Submit connection_type = cloud
print("=== Submitting connection_type: cloud ===")
result = api(f"config/config_entries/flow/{FLOW_ID}", method="POST", data={
    "connection_type": "cloud"
})
print(f"  Type: {result.get('type')}")
print(f"  Step: {result.get('step_id')}")

if result.get("type") == "external_step":
    url = result.get("url", "")
    print(f"\n  === AUTHORIZATION REQUIRED ===")
    print(f"  Open this URL in your browser:")
    print(f"  {url}")
    print(f"\n  After authorizing with Yandex, the flow will complete.")
    print(f"  You can check status by running the script again after auth.")
elif result.get("type") == "form":
    schema = result.get("data_schema", [])
    print(f"  Form fields: {[s.get('name') for s in schema]}")
    placeholders = result.get("description_placeholders", {})
    for k, v in placeholders.items():
        print(f"  {k}: {v}")
elif result.get("type") == "create_entry":
    print(f"\n  Integration created!")
    print(f"  {json.dumps(result, ensure_ascii=False)[:500]}")
else:
    print(f"  Full result: {json.dumps(result, ensure_ascii=False)[:500]}")
