import paramiko, json, time, urllib.request

TOKEN = 'CHANGE_ME'

print("Waiting 60s for HA to start...")
time.sleep(60)

def api(path, method="GET", data=None):
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(f"http://192.168.1.92:8123/api/{path}", data=body, headers=headers, method=method)
    return json.load(urllib.request.urlopen(req, timeout=15))

for attempt in range(10):
    try:
        config = api("config")
        components = config.get("components", [])
        yash = [c for c in components if "yandex" in c.lower()]
        print(f"HA v{config.get('version')} UP!")
        print(f"Yandex components: {yash}")

        # Check if yandex_station domain exists in config entries
        entries = api("config/config_entries/entry")
        yash_entries = [e for e in entries if "yandex" in e.get("domain","")]
        print(f"\nYandex config entries:")
        for e in yash_entries:
            print(f"  {e['domain']}: {e.get('title','')} (state={e.get('state','')})")

        # Try starting yandex_station config flow
        print("\n=== Starting yandex_station config flow ===")
        result = api("config/config_entries/flow", method="POST", data={
            "handler": "yandex_station",
            "show_advanced_options": True
        })
        flow_id = result.get("flow_id", "")
        print(f"  Flow ID: {flow_id}")
        print(f"  Step: {result.get('step_id')}")
        print(f"  Result: {json.dumps(result, ensure_ascii=False)[:600]}")
        break
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        if "Invalid handler" in body:
            print(f"  Attempt {attempt+1}: yandex_station not loaded - {body[:200]}")
        else:
            print(f"  Attempt {attempt+1}: HTTP {e.code}")
        time.sleep(15)
    except Exception as e:
        print(f"  Attempt {attempt+1}: {e}")
        time.sleep(15)
