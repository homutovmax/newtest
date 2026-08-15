import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=10)

# Check the pipeline.py on the server
stdin, stdout, stderr = ssh.exec_command("docker exec hr-web-1 cat /app/src/pipeline.py 2>&1 | head -65")
print('=== SERVER pipeline.py (lines 1-65) ===')
print(stdout.read().decode('utf-8', errors='replace'))

# Check src directory
stdin, stdout, stderr = ssh.exec_command("docker exec hr-web-1 ls -la /app/src/ 2>&1")
print('\n=== SERVER src/ ===')
print(stdout.read().decode('utf-8', errors='replace'))

# Check if there's an update_vacancies.py in the container
stdin, stdout, stderr = ssh.exec_command("docker exec hr-web-1 ls -la /app/update_vacancies.py 2>&1; echo ==; docker exec hr-web-1 wc -l /app/update_vacancies.py 2>&1")
print('\n=== UPDATE VACANCIES ===')
print(stdout.read().decode('utf-8', errors='replace'))

ssh.close()
