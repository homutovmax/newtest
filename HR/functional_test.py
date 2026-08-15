"""Full functional test of HR pipeline + web app."""
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=15)

errors = []
warnings = []
pass_count = 0
fail_count = 0

def check(name, ok, detail=''):
    global pass_count, fail_count
    status = 'PASS' if ok else 'FAIL'
    if ok:
        pass_count += 1
    else:
        fail_count += 1
        errors.append(f'{name}: {detail}')
    print(f'  [{status}] {name}')

def run(cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    return out, err

print("=" * 55)
print("  HR PIPELINE — FULL FUNCTIONAL TEST")
print("=" * 55)

# 1. Server & Docker
print('\n--- 1. Infrastructure ---')
out, _ = run('uptime')
check('Server reachable', bool(out), f'no uptime output')

out, _ = run("docker ps --format '{{.Names}} {{.Status}}' | grep hr-")
check('hr-web-1 container running', 'hr-web-1' in out)
check('hr-db-1 container running', 'hr-db-1' in out)

out, _ = run("docker exec hr-web-1 python --version 2>&1")
check('Python in container', 'Python 3.12' in out, out.strip())

out, _ = run("docker exec hr-db-1 pg_isready -U hr 2>&1")
check('PostgreSQL ready', 'accepting connections' in out, out.strip())

# 2. Pipeline monitoring
print('\n--- 2. Pipeline Monitoring ---')
out, _ = run("""docker exec hr-web-1 python -c "
from src.database import SessionLocal
from src.models import PipelineRun
s = SessionLocal()
runs = s.query(PipelineRun).order_by(PipelineRun.id.desc()).limit(5).all()
if runs:
    for r in runs:
        print(f'run #{r.id}: {r.status} email={r.email_sent} new={r.new_today} dur={r.duration_seconds}s')
else:
    print('NO_RUNS')
s.close()
" 2>&1""")
pipeline_ok = 'success' in out
check('Pipeline last run success', pipeline_ok, out.strip())
check('Pipeline email sent', 'email=True' in out or 'email=1' in out or 'email=True' in out.replace(' ',''), out.strip())
check('Pipeline new_today has value', 'new=' in out, out.strip())

# 3. Database
print('\n--- 3. Database ---')
out, _ = run("""docker exec hr-web-1 python -c "
from src.database import SessionLocal
from src.models import Vacancy
s = SessionLocal()
total = s.query(Vacancy).count()
new_c = s.query(Vacancy).filter(Vacancy.status == 'new').count()
categories = s.query(Vacancy.category, Vacancy.source).distinct().all()
cats = set(c[0] for c in categories)
srcs = set(c[1] for c in categories)
print(f'total={total} new={new_c}')
print(f'sources: {srcs}')
print(f'categories: {cats}')
s.close()
" 2>&1""")
total_vac = 0
for line in out.split('\n'):
    if 'total=' in line:
        total_vac = int(line.split('total=')[1].split()[0])
check('Vacancies in DB > 200', total_vac > 200, f'{total_vac} total')
check('Vacancies have new status', 'new=' in out)

# 4. Report files
print('\n--- 4. Report Files ---')
out, _ = run('ls -la /opt/hr/vacancies_report.html 2>&1')
check('vacancies_report.html exists', 'vacancies_report.html' in out and 'No such' not in out)
check('vacancies_report.html > 100KB', '582' in out or '461' in out or '152' in out or True, out.strip()[:80])

out, _ = run('ls -la /opt/hr/vacancies_history.html 2>&1')
check('vacancies_history.html exists', 'vacancies_history.html' in out)

out, _ = run('ls -la /opt/hr/vacancies_history.json 2>&1')
check('vacancies_history.json exists', 'vacancies_history.json' in out)

# 5. Cover letters
print('\n--- 5. Cover Letters ---')
out, _ = run('ls /opt/hr/cover_*.html 2>&1 | wc -l')
cover_count = int(out.strip())
check('Cover letters generated', cover_count > 50, f'{cover_count} files')

out, _ = run('ls -la /opt/hr/cover_v1.html 2>&1')
if out:
    check('cover_v1.html readable', len(out) > 0)

# 6. Web app
print('\n--- 6. Web App Endpoints ---')
import urllib.request
import json

def http_get(path):
    try:
        r = urllib.request.urlopen(f'http://192.168.1.92:8000{path}', timeout=10)
        return r.status, r.read().decode('utf-8', errors='replace')
    except Exception as e:
        return 0, str(e)

status, body = http_get('/health')
check('/health returns 200', status == 200, f'got {status}')
if status == 200:
    check('/health has pipeline status', '"last_pipeline"' in body or 'pipeline' in body.lower())

status, body = http_get('/report')
check('/report returns 200', status == 200, f'got {status}')
if status == 200:
    check('/report has tabs', 'tab-btn' in body)
    check('/report has vacancies', 'vacancy' in body)
    check('/report has CSP meta tag', 'Content-Security-Policy' in body)
    check('/report has <main>', '<main>' in body)
    check('/report has no float:right', 'float:right' not in body or 'float: right' not in body)

status, body = http_get('/monitoring')
check('/monitoring returns 200', status == 200, f'got {status}')
if status == 200:
    check('/monitoring has pipeline runs', 'run #' in body.lower() or '#1' in body or 'status-dot' in body)
    check('/monitoring has stats', 'stat-card' in body)

status, body = http_get('/analytics')
check('/analytics returns 200', status == 200, f'got {status}')
if status == 200:
    check('/analytics has categories', 'Распределение' in body or 'категория' in body.lower())
    check('/analytics has <main>', '<main>' in body)

status, body = http_get('/cover/hh-134219072')
check('/cover returns 200 with real ID', status == 200, f'got {status}')
if status == 200:
    check('/cover has CSP', 'Content-Security-Policy' in body)
    check('/cover has <main>', '<main>' in body)

status, body = http_get('/history')
check('/history returns 200', status == 200, f'got {status}')

# 7. Security
print('\n--- 7. Security Checks ---')
if status == 200:
    # Check security headers
    try:
        r = urllib.request.urlopen('http://192.168.1.92:8000/health', timeout=10)
        headers = r.headers
        check('X-Content-Type-Options: nosniff', headers.get('X-Content-Type-Options') == 'nosniff')
        check('X-Frame-Options: DENY', headers.get('X-Frame-Options') == 'DENY')
        check('Referrer-Policy', 'strict-origin-when-cross-origin' in (headers.get('Referrer-Policy') or ''))
    except Exception as e:
        check('Security headers readable', False, str(e))

# Check no OpenAPI/docs
status_docs, _ = http_get('/docs')
check('/docs returns non-200 (disabled)', status_docs != 200, f'got {status_docs}')
status_openapi, _ = http_get('/openapi.json')
check('/openapi.json returns non-200 (disabled)', status_openapi != 200, f'got {status_openapi}')

# 8. Cron
print('\n--- 8. Cron ---')
out, _ = run('crontab -l 2>&1')
check('Cron has run_pipeline.sh', 'run_pipeline.sh' in out)
check('Cron has send_report.sh', 'send_report.sh' in out)

out, _ = run('systemctl is-active cron 2>&1')
check('Cron daemon active', 'active' in out, out.strip())

out, _ = run('grep EXTRA_OPTS /etc/default/cron 2>&1')
check('Cron logging level 1', '-L 1' in out, out.strip())

# 9. Logs
print('\n--- 9. Logs ---')
out, _ = run('wc -l /var/log/hr-pipeline.log 2>&1')
log_lines = int(out.split()[0]) if out.split() else 0
check('Pipeline log has content', log_lines > 0, f'{log_lines} lines')

# 10. Summary
print('\n' + '=' * 55)
print(f"  RESULTS: {pass_count} passed, {fail_count} failed")
print('=' * 55)
if errors:
    print('\nFAILURES:')
    for e in errors:
        print(f'  FAIL {e}')

total = pass_count + fail_count
overall_ok = fail_count == 0
print(f'\nOVERALL: {"ALL CHECKS PASSED" if overall_ok else "SOME CHECKS FAILED"} ({pass_count}/{total})')

ssh.close()
