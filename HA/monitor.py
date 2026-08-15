import paramiko, json, urllib.request, datetime, sys

TOKEN = 'CHANGE_ME'
HOST = '192.168.1.92'
USER = 'root'
PASS = 'CHANGE_ME'

CRITICAL_INTTEGRATIONS = [
    'yandex_station',
    'mqtt',
    'zha',
    'google_translate',
    'mobile_app',
]

def log(msg):
    ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f'[{ts}] {msg}')

def api(path):
    headers = {'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json'}
    req = urllib.request.Request(f'http://192.168.1.92:8123/api/{path}', headers=headers)
    return json.load(urllib.request.urlopen(req, timeout=15))

def restart_ha():
    log('Перезапуск Home Assistant...')
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PASS, timeout=10)
    stdin, stdout, stderr = ssh.exec_command('docker restart homeassistant', timeout=60)
    out = stdout.read().decode()
    log(f'Результат рестарта: {out.strip()}')
    ssh.close()

def check_integrations():
    entries = api('config/config_entries/entry')
    failed = []
    loaded = []
    not_loaded = []
    
    for e in entries:
        domain = e.get('domain', '')
        state = e.get('state', '')
        title = e.get('title', '')
        
        if state == 'failed_unload' or state == 'error':
            failed.append(f'{domain} ({title}) state={state}')
        elif state == 'not_loaded':
            not_loaded.append(f'{domain} ({title})')
        elif state == 'loaded':
            loaded.append(domain)
    
    return loaded, failed, not_loaded

def check_entities(entity_ids):
    states = api('states')
    state_map = {s['entity_id']: s for s in states}
    unavailable = []
    for eid in entity_ids:
        s = state_map.get(eid)
        if s and s['state'] in ('unavailable', 'unknown', ''):
            unavailable.append(f'{eid} = {s["state"]}')
    return unavailable

def check_api():
    try:
        config = api('config')
        return True, config.get('version', '?')
    except Exception as e:
        return False, str(e)

# Main
log('=== Проверка системы ===')

# 1. API check
api_ok, version = check_api()
if not api_ok:
    log(f'КРИТИЧНО: HA API не отвечает! Ошибка: {version}')
    restart_ha()
    sys.exit(1)
log(f'HA API OK (v{version})')

# 2. Integration states
loaded, failed, not_loaded = check_integrations()
log(f'Интеграций загружено: {len(loaded)}')

if failed:
    log(f'КРИТИЧНО: Сломанные интеграции ({len(failed)}):')
    for f in failed:
        log(f'  - {f}')
    
    # Check if critical integrations are in failed list
    critical_failed = [f for f in failed if any(c in f for c in CRITICAL_INTTEGRATIONS)]
    if critical_failed:
        log(f'Критические интеграции сломаны: {critical_failed}')
        restart_ha()
    else:
        log('Некритические интеграции сломаны, рестарт не требуется')
else:
    log('Все интеграции в порядке')

if not_loaded:
    log(f'Не загружены ({len(not_loaded)}):')
    for n in not_loaded:
        log(f'  - {n}')

# 3. Key entity check
key_entities = [
    'sensor.datchik_kachestva_vozdukha_eco2',
    'media_player.yandex_station_r1099440084h0y',
    'automation.mclh08_eco2_alert',
]
unavailable = check_entities(key_entities)
if unavailable:
    log(f'Недоступные сущности:')
    for u in unavailable:
        log(f'  - {u}')
else:
    log('Все ключевые сущности доступны')

log('=== Проверка завершена ===')
