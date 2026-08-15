#!/usr/bin/env python3
"""Deploy HR project files to Beget via SFTP."""
import paramiko, os

HOST = 'maximum64.beget.tech'
PORT = 22
USER = 'maximum64'
PASS = 'yIqC1N!NyAqO'

FILES = {
    # local -> remote
    'vacancies_report.html': '~/maximum64.beget.tech/public_html/vacancies_report.html',
    'vacancies_history.json': '~/hr_bot/vacancies_history.json',
    'vacancies_history.html': '~/maximum64.beget.tech/public_html/vacancies_history.html',
    'update_vacancies.py': '~/hr_bot/update_vacancies.py',
    'tg_bot.py': '~/hr_bot/tg_bot.py',
    'generate_cover.py': '~/maximum64.beget.tech/public_html/generate_cover.py',
    'resume.php': '~/maximum64.beget.tech/public_html/resume.php',
    'resume_ai.php': '~/maximum64.beget.tech/public_html/resume_ai.php',
    'vacancies_analytics.html': '~/maximum64.beget.tech/public_html/vacancies_analytics.html',
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, PORT, USER, PASS)
sftp = ssh.open_sftp()

for local, remote in FILES.items():
    local_path = os.path.join(BASE_DIR, local)
    if not os.path.exists(local_path):
        print(f'SKIP (not found): {local}')
        continue
    remote = remote.replace('~/', '/home/m/' + USER + '/')
    # Ensure dir exists
    rdir = os.path.dirname(remote)
    try:
        sftp.stat(rdir)
    except FileNotFoundError:
        sftp.mkdir(rdir)
    with sftp.open(remote, 'wb') as f:
        with open(local_path, 'rb') as lf:
            f.write(lf.read())
    print(f'OK: {local} -> {remote}')

sftp.close()
ssh.close()
print('DONE')
