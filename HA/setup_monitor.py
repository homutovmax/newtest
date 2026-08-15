import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)
sftp = ssh.open_sftp()

monitor_script = r"""#!/usr/bin/env python3
""" + '"""' + r"""
Monitor HA integrations and auto-restart on failures.
Run via cron: */5 * * * * /usr/bin/python3 /opt/ha_monitor.py >> /var/log/ha_monitor.log 2>&1
""" + '"""' + r"""

import json, urllib.request, subprocess, datetime, sys, os

TOKEN = 'CHANGE_ME'
LOG = '/var/log/ha_monitor.log'
STATE_FILE = '/opt/ha_monitor_state.json'

CRITICAL = ['yandex_station', 'mqtt', 'zha', 'google_translate', 'mobile_app']

def log(msg):
    ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f'[{ts}] {msg}'
    print(line)
    with open(LOG, 'a') as f:
        f.write(line + '\n')

def api(path):
    req = urllib.request.Request(f'http://localhost:8123/api/{path}',
        headers={'Authorization': f'Bearer {TOKEN}'})
    return json.load(urllib.request.urlopen(req, timeout=15))

def load_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except:
        return {'restart_count': 0, 'last_restart': None, 'cooldown_until': None}

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

def restart_ha():
    state = load_state()
    now = datetime.datetime.now().isoformat()
    
    # Cooldown: max 3 restarts per hour
    if state.get('cooldown_until'):
        if datetime.datetime.now().isoformat() < state['cooldown_until']:
            log('Кулдаун: пропускаю рестарт')
            return False
    
    if state.get('last_restart'):
        last = datetime.datetime.fromisoformat(state['last_restart'])
        if (datetime.datetime.now() - last).total_seconds() < 3600:
            state['restart_count'] = state.get('restart_count', 0) + 1
        else:
            state['restart_count'] = 1
    else:
        state['restart_count'] = 1
    
    if state['restart_count'] > 3:
        state['cooldown_until'] = (datetime.datetime.now() + datetime.timedelta(hours=1)).isoformat()
        save_state(state)
        log('Превышен лимит рестартов (3/час). Кулдаун 1 час.')
        return False
    
    log('Перезапуск Home Assistant...')
    subprocess.run(['docker', 'restart', 'homeassistant'], capture_output=True, timeout=120)
    state['last_restart'] = now
    save_state(state)
    log('Home Assistant перезапущен')
    return True

# Main check
log('--- Проверка ---')

# 1. API
try:
    config = api('config')
    log(f'API OK (v{config.get("version","?")})')
except Exception as e:
    log(f'КРИТИЧНО: API не отвечает: {e}')
    restart_ha()
    sys.exit(1)

# 2. Integrations
entries = api('config/config_entries/entry')
failed = [e for e in entries if e.get('state') in ('failed_unload', 'error')]
critical_failed = [e for e in failed if any(c in e.get('domain','') for c in CRITICAL)]

if critical_failed:
    for f in critical_failed:
        log(f'КРИТИЧНО: {f["domain"]} ({f.get("title","")}) = {f["state"]}')
    restart_ha()
elif failed:
    for f in failed:
        log(f'ПРЕДУПРЕЖДЕНИЕ: {f["domain"]} ({f.get("title","")}) = {f["state"]}')
else:
    log(f'Интеграции OK ({len(entries)} загружено)')

# 3. Key entities
key = ['sensor.datchik_kachestva_vozdukha_eco2', 'media_player.yandex_station_r1099440084h0y']
states = api('states')
sm = {s['entity_id']: s for s in states}
for eid in key:
    s = sm.get(eid)
    if s and s['state'] in ('unavailable', 'unknown'):
        log(f'Недоступна: {eid} = {s["state"]}')
    elif s:
        pass  # ok

log('--- OK ---')
"""

with sftp.open('/opt/ha_monitor.py', 'w') as f:
    f.write(monitor_script.encode('utf-8'))

# Make executable
stdin, stdout, stderr = ssh.exec_command('chmod +x /opt/ha_monitor.py && touch /var/log/ha_monitor.log')
print(stdout.read().decode())
print(stderr.read().decode())

# Add cron job (every 5 minutes)
cron_line = '*/5 * * * * /usr/bin/python3 /opt/ha_monitor.py >> /var/log/ha_monitor.log 2>&1'
cmd = f'(crontab -l 2>/dev/null | grep -v ha_monitor; echo "{cron_line}") | crontab -'
stdin, stdout, stderr = ssh.exec_command(cmd)
print(stdout.read().decode())
print(stderr.read().decode())

# Verify cron
stdin, stdout, stderr = ssh.exec_command('crontab -l | grep ha_monitor')
print(f'Cron: {stdout.read().decode().strip()}')

# First run test
stdin, stdout, stderr = ssh.exec_command('python3 /opt/ha_monitor.py', timeout=30)
print(stdout.read().decode())
print(stderr.read().decode())

sftp.close()
ssh.close()
print('\nМониторинг настроен! Каждые 5 минут проверяет интеграции.')
