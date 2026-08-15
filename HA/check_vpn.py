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

# Check if any VPN tools exist
print("=== VPN tools ===")
for c in ['which wireguard 2>/dev/null', 'which wg 2>/dev/null', 'which wg-quick 2>/dev/null',
          'which openvpn 2>/dev/null', 'which 3proxy 2>/dev/null', 'which squid 2>/dev/null',
          'test -f /usr/sbin/wireguard', 'test -f /usr/bin/wg', 'ip link show 2>/dev/null | grep -i wg',
          'lsmod 2>/dev/null | grep wireguard', 'which proxychains 2>/dev/null',
          'docker ps --format "{{.Names}}" 2>/dev/null | grep -i -E "vpn|proxy|wire|wg|openvpn|3proxy"',
          'docker ps -a --format "{{.Names}}" 2>/dev/null | grep -i -E "vpn|proxy|wire|wg|openvpn"']:
    out = run(c, 10)
    print(f"  {c}: {out[:200] if out else '(empty/not found)'}")

# Check network environment
print("\n=== Network info ===")
gw = run("ip route 2>/dev/null | head -3", 10)
print(f"  Default route: {gw}")

# Check if there's already a proxy configured
print("\n=== Proxy settings ===")
for f in ['/etc/environment', '/etc/profile', '/etc/bash.bashrc', '/root/.bashrc']:
    out = run(f"grep -i proxy {f} 2>/dev/null", 10)
    if out and 'ERR' not in out:
        print(f"  {f}: {out[:500]}")

# Check if HA has proxy env
print("\n=== HA container proxy ===")
ha_env = run("docker inspect homeassistant --format '{{json .Config.Env}}' 2>/dev/null | tr ',' '\n' | grep -i proxy", 10)
print(f"  HA proxy env: {ha_env[:500] if ha_env else '(none)'}")

# Check DNS settings
print("\n=== DNS ===")
dns = run("cat /etc/resolv.conf 2>/dev/null", 10)
print(f"  resolv.conf: {dns[:500]}")
dns2 = run("docker inspect homeassistant --format '{{json .HostConfig.Dns}}' 2>/dev/null", 10)
print(f"  HA DNS: {dns2[:200] if dns2 else '(default)'}")

# Try different DNS
print("\n=== DNS test ===")
for dns_srv in ['1.1.1.1', '8.8.8.8', '77.88.8.8']:
    out = run(f"nslookup haieriot.com {dns_srv} 2>&1 | head -5", 10)
    print(f"  {dns_srv}: {out[:300]}")

# Check if haier is reachable from outside (try public DNS)
print("\n=== Try via alternative DNS ===")
out = run("curl -s --dns-servers 1.1.1.1 -o /dev/null -w '%{http_code}' --connect-timeout 10 https://haieriot.com/ 2>&1", 15)
print(f"  curl with 1.1.1.1: {out}")

# Can we reach internet at all?
print("\n=== General internet ===")
for site in ['https://google.com', 'https://cloudflare.com']:
    out = run(f"curl -s -o /dev/null -w '%{{http_code}}' --connect-timeout 10 {site} 2>&1", 15)
    print(f"  {site}: {out}")

ssh.close()
