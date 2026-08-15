import paramiko, json, time, urllib.request

HOST = '192.168.1.92'
USER = 'root'
PASS = 'CHANGE_ME'
TOKEN = 'CHANGE_ME'

print("Waiting 60s for HA to fully start...")
time.sleep(60)

for attempt in range(10):
    try:
        req = urllib.request.Request("http://192.168.1.92:8123/api/config",
            headers={"Authorization": f"Bearer {TOKEN}"})
        config = json.load(urllib.request.urlopen(req, timeout=10))
        components = config.get("components", [])
        yash = [c for c in components if "yandex" in c.lower()]
        print(f"HA UP! version={config.get('version')}")
        print(f"Yandex components: {yash}")

        # Try config flow
        req2 = urllib.request.Request("http://192.168.1.92:8123/api/config/config_entries/flow",
            data=json.dumps({"handler": "yandex_smart_home", "show_advanced_options": True}).encode(),
            headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
            method="POST")
        result = json.load(urllib.request.urlopen(req2, timeout=15))
        print(f"Config flow: {json.dumps(result, ensure_ascii=False)[:500]}")
        break
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        if "Invalid handler" in body:
            print(f"  Attempt {attempt+1}: yandex_smart_home not loaded - {body[:200]}")
        else:
            print(f"  Attempt {attempt+1}: HTTP {e.code} - {body[:200]}")
        time.sleep(15)
    except Exception as e:
        print(f"  Attempt {attempt+1}: {e}")
        time.sleep(15)
