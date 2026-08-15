import paramiko

HOST = '192.168.1.92'
USER = 'root'
PASS = 'CHANGE_ME'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=15)

def run(cmd, timeout=15):
    try:
        stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
        return stdout.read().decode('utf-8', errors='replace').strip()
    except Exception as e:
        return f'ERR: {e}'

print("=== 1. Docker контейнеры (LLM/AI/ML) ===")
all_containers = run("docker ps -a --format '{{.Names}}' 2>&1", 10)
print(all_containers)
# Check for LLM-related containers
for name in all_containers.split('\n'):
    name_lower = name.lower().strip()
    if any(kw in name_lower for kw in ['llm', 'ollama', 'openai', 'localai', 'llama', 'cortex', 'gpt', 'transformers', 'text-generation', 'vllm', 'tgi', 'whisper', 'stability', 'diffusion', 'comfy', 'invokeai']):
        print(f"  >>> LLM-related: {name}")

print("\n=== 2. Docker образы (LLM/AI) ===")
images = run("docker images --format '{{.Repository}} {{.Tag}} {{.Size}}' 2>&1", 10)
print(images if images else "(none)")
for line in images.split('\n'):
    if any(kw in line.lower() for kw in ['llm', 'ollama', 'openai', 'localai', 'llama', 'cortex', 'gpt', 'transformers', 'text-generation', 'vllm', 'tgi', 'whisper', 'stability', 'diffusion', 'comfy', 'invokeai', 'nvidia', 'cuda', 'pytorch', 'tensorflow', 'ghcr', 'lmsys', 'huggingface']):
        print(f"  >>> LLM-related: {line}")

print("\n=== 3. Docker volumes (LLM) ===")
volumes = run("docker volume ls --format '{{.Name}}' 2>&1", 10)
for vol in volumes.split('\n'):
    if any(kw in vol.lower() for kw in ['llm', 'ollama', 'openai', 'localai', 'llama', 'cortex', 'model', 'cuda', 'nvidia', 'huggingface', 'cache']):
        print(f"  >>> LLM-related volume: {vol}")

print("\n=== 4. Docker сети (LLM) ===")
networks = run("docker network ls --format '{{.Name}}' 2>&1", 10)
for net in networks.split('\n'):
    if any(kw in net.lower() for kw in ['llm', 'ollama', 'openai', 'localai', 'llama', 'ai']):
        print(f"  >>> LLM-related network: {net}")

print("\n=== 5. Поиск LLM файлов в /DATA ===")
print(run("find /DATA -maxdepth 4 -type d -iname '*ollama*' -o -type d -iname '*llama*' -o -type d -iname '*localai*' -o -type d -iname '*cortex*' -o -type d -iname '*openai*' -o -type d -iname '*model*' 2>/dev/null | grep -v node_modules | grep -v '.pnpm' | head -20", 15))

print("\n=== 6. Поиск больших model файлов ===")
print(run("find /DATA -name '*.gguf' -o -name '*.bin' -o -name '*.safetensors' -o -name '*.pth' -o -name '*.pt' -o -name '*.onnx' 2>/dev/null | head -20", 15))

print("\n=== 7. Проверка портов (LLM сервисы) ===")
print(run("ss -tlnp 2>/dev/null | grep -E '11434|8080|8000|9090|5000|8888' | head -10", 10))

print("\n=== 8. Поиск в AppData каталогов ===")
appdata = run("ls -la /DATA/AppData/ 2>&1", 5)
print(appdata)
for entry in appdata.split('\n'):
    entry_lower = entry.lower()
    if any(kw in entry_lower for kw in ['llm', 'ollama', 'localai', 'llama', 'cortex', 'openai', 'model', 'ai']):
        print(f"  >>> LLM-related AppData: {entry}")

print("\n=== 9. Проверка systemd сервисов ===")
print(run("systemctl list-units --type=service --all 2>/dev/null | grep -iE 'ollama|llama|localai|cortex|openai|whisper' | head -10", 10))

print("\n=== 10. Проверка процессов ===")
print(run("ps aux 2>/dev/null | grep -iE 'ollama|llama|localai|cortex|python.*llm|openai' | grep -v grep | head -10", 10))

print("\n=== 11. Docker Compose файлы ===")
print(run("find /DATA -name 'docker-compose*.yml' -o -name 'compose*.yml' 2>/dev/null | head -10", 10))
for cf in run("find /DATA -name 'docker-compose*.yml' -o -name 'compose*.yml' 2>/dev/null", 10).split('\n'):
    if cf.strip():
        content = run(f"head -30 {cf.strip()} 2>/dev/null", 5)
        if any(kw in content.lower() for kw in ['ollama', 'openai', 'llama', 'localai', 'cortex', 'nvidia', 'cuda']):
            print(f"  >>> LLM-related compose: {cf.strip()}")

print("\n=== ПОИСК ЗАВЕРШЁН ===")
ssh.close()
