import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)
sftp = ssh.open_sftp()

# Read the server's update_vacancies.py
with sftp.open('/opt/hr/update_vacancies.py', 'rb') as f:
    content = f.read().decode('utf-8')

lines = content.split('\n')
print(f'Server file: {len(lines)} lines')

# Fix esc() - handle non-string types
# Find the esc() function definition
fixes = 0
for i, line in enumerate(lines):
    if line.strip().startswith('def esc('):
        # After this line, find the return statement and fix it
        for j in range(i, min(i+10, len(lines))):
            if 'html_mod.escape(s or' in lines[j]:
                old = lines[j]
                lines[j] = lines[j].replace('html_mod.escape(s or', 'html_mod.escape(str(s or')
                print(f'  Fixed esc() line {j+1}: {old.strip()} -> {lines[j].strip()}')
                fixes += 1
                break
        break

# Fix vac_card() salary line
for i, line in enumerate(lines):
    if 'esc(v.get(' in line and 'salary' in line:
        old = line
        lines[i] = line.replace('esc(v.get(', 'esc(str(v.get(')
        print(f'  Fixed vac_card line {i+1}: {old.strip()} -> {lines[i].strip()}')
        fixes += 1
        break

# Add __name__ guard before the main execution block
# Find "seen_keys = set()" or "all_vacancies = []" - start of execution code
exec_markers = [
    'seen_keys = set()',
    'all_vacancies = []',
    "sber_count = 0",
    "log('rabota.sber.ru",
]
guard_added = False
for i, line in enumerate(lines):
    if any(m in line for m in exec_markers) and not line.strip().startswith('#'):
        # Check if __name__ guard already exists
        has_guard = any('if __name__' in l for l in lines[max(0,i-5):i+5])
        if not has_guard:
            # Find the function boundaries - add guard before execution code
            indent = len(line) - len(line.lstrip())
            lines.insert(i, '\n# === main execution (guarded) ===')
            lines.insert(i+1, 'if __name__ == "__main__":')
            guard_added = True
            print(f'  Added __name__ guard before line {i+1}: {line.strip()[:60]}')
            break
        else:
            print('  __name__ guard already exists')
        break

# Write back
new_content = '\n'.join(lines)
with sftp.open('/opt/hr/update_vacancies.py', 'wb') as f:
    f.write(new_content.encode('utf-8'))

print(f'\nFixes applied: {fixes} + guard={guard_added}')

# Verify
stdin, stdout, stderr = ssh.exec_command("grep -n 'if __name__' /opt/hr/update_vacancies.py")
print('\n=== GUARD CHECK ===')
print(stdout.read().decode('utf-8', errors='replace'))

stdin, stdout, stderr = ssh.exec_command("sed -n '65,80p' /opt/hr/update_vacancies.py")
print('=== esc() CHECK ===')
print(stdout.read().decode('utf-8', errors='replace'))

sftp.close()
ssh.close()
