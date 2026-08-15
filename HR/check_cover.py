import urllib.request
r = urllib.request.urlopen('http://192.168.1.92:8000/cover/v1', timeout=10)
body = r.read().decode('utf-8')
print(f'Status: {r.status}')
print(f'Length: {len(body)}')
print(f'Has cover-container: {"cover-container" in body}')
print(f'Has <main>: {"<main>" in body}')
print(f'First 200 chars:', body[:200])
