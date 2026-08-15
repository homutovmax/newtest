import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('192.168.1.92', username='root', password='CHANGE_ME', timeout=15)

def run(cmd, timeout=15):
    try:
        stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
        return stdout.read().decode('utf-8', errors='replace').strip()
    except Exception as e:
        return f'ERR: {e}'

print("=== Проверка доступа к Docker Hub ===")
print("1. DNS resolution:")
print(run("nslookup registry.hub.docker.com 2>&1 | head -10", 10))
print(run("nslookup registry-1.docker.io 2>&1 | head -10", 10))

print("\n2. Ping:")
print(run("ping -c 2 -W 3 registry.hub.docker.com 2>&1", 10))

print("\n3. Curl (HTTPS):")
print(run("curl -s -o /dev/null -w '%{http_code}' --connect-timeout 5 https://registry.hub.docker.com/v2/ 2>&1", 10))

print("\n4. Curl docker.io:")
print(run("curl -s -o /dev/null -w '%{http_code}' --connect-timeout 5 https://registry-1.docker.io/v2/ 2>&1", 10))

print("\n5. Из самого HA контейнера:")
print(run("docker exec homeassistant curl -s -o /dev/null -w '%{http_code}' --connect-timeout 10 https://registry.hub.docker.com/v2/ 2>&1", 15))

print("\n6. Проверка DNS через HA:")
print(run("docker exec homeassistant nslookup registry.hub.docker.com 2>&1 | head -10", 15))

print("\n7. Проверка network HA:")
print(run("docker inspect homeassistant --format '{{json .HostConfig.NetworkMode}}' 2>&1", 5))
print(run("docker inspect homeassistant --format '{{range $k,$v := .NetworkSettings.Networks}}{{$k}}: {{$v.IPAddress}}{{\"\\n\"}}{{end}}' 2>&1", 5))

ssh.close()
