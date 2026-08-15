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

TOKEN = "CHANGE_ME"

# Check Docker hub entity details
print("=== Docker Hub entity ===")
state = run("curl -s -H 'Authorization: Bearer " + TOKEN + "' http://localhost:8123/api/states/sensor.docker_hub 2>&1 | python3 -m json.tool 2>/dev/null | head -30", 15)
print(state)

print("\n=== Docker Hub binary sensor ===")
state2 = run("curl -s -H 'Authorization: Bearer " + TOKEN + "' http://localhost:8123/api/states/binary_sensor.docker_hub_update_available 2>&1 | python3 -m json.tool 2>/dev/null | head -30", 15)
print(state2)

# Check what wud (WhatsUpDocker) is - it manages docker updates
print("\n=== wud container ===")
info = run("docker inspect wud --format 'Image: {{.Config.Image}}' 2>&1", 10)
print(info)

print("\n=== wud ports ===")
ports = run("docker port wud 2>&1", 5)
print(ports)

print("\n=== wud logs (errors) ===")
logs = run("docker logs wud --tail 30 2>&1 | grep -iE 'error|warn|fail|hub|docker' | tail -10", 15)
print(logs if logs else '(нет ошибок)')

# Check wud for docker hub configuration
print("\n=== wud environment ===")
env = run("docker inspect wud --format '{{range $k, $v := .Config.Env}}{{println $v}}{{end}}' 2>&1", 10)
print(env[:2000])

# Check the docker hub integration in HA
print("\n=== HA config entries for docker_hub ===")
entries = run("curl -s -H 'Authorization: Bearer " + TOKEN + "' http://localhost:8123/api/config/config_entries/entry 2>&1 | python3 -c \"import sys,json; d=json.load(sys.stdin); [print(json.dumps(e,indent=2)) for e in (d if isinstance(d,list) else []) if 'docker' in str(e).lower()]\" 2>/dev/null", 15)
print(entries[:2000])

# Check wud health
print("\n=== wud health ===")
health = run("docker inspect wud --format '{{.State.Status}}, Health: {{.State.Health.Status}}' 2>&1", 10)
print(health)

# Check if docker socket is mounted to wud
print("\n=== wud mounts ===")
mounts = run("docker inspect wud --format '{{range .Mounts}}{{.Source}} -> {{.Destination}}{{\"\\n\"}}{{end}}' 2>&1", 10)
print(mounts)

ssh.close()
