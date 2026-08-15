import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=15)

def run(cmd, timeout=10):
    try:
        stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
        return stdout.read().decode('utf-8', errors='replace').strip()
    except Exception as e:
        return f'ERR: {e}'

# Read current HA configuration to see if templates already exist
print("=== Проверка configuration.yaml ===")
conf = run("docker exec homeassistant cat /config/configuration.yaml 2>&1", 10)
print(conf)

# Check if there's already template or sensor configuration
print("\n=== Поиск template в HA ===")
templates = run("docker exec homeassistant find /config -name 'configuration.yaml' -exec grep -l 'template\\|sensor:' {} \\; 2>&1", 10)
print(templates)

# Check automations for temperature
print("\n=== automations.yaml ===")
auto = run("docker exec homeassistant cat /config/automations.yaml 2>&1 | head -40", 10)
print(auto)

# Check if there's sensors.yaml
print("\n=== sensors.yaml ===")
sens = run("docker exec homeassistant cat /config/sensors.yaml 2>&1", 10)
print(sens[:1000] if sens else '(нет файла)')

ssh.close()
