import paramiko, json, sys, time, uuid

HOST = '192.168.1.92'
USER = 'root'
PASS = 'CHANGE_ME'

topic = sys.argv[1]
filter_keywords = ['device_joined', 'device_announce', 'device_interview', 'MCLH', 'LifeControl', 'permit_join']
timeout = int(sys.argv[2]) if len(sys.argv) > 2 else 60

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS, timeout=10)

# Start docker logs -f in background
outfile = f'/tmp/z2m_monitor_{uuid.uuid4().hex[:8]}.log'
run_cmd = f'docker logs big-bear-zigbee2mqtt --tail 50 -f > {outfile} 2>&1 & echo PID=$!'
stdin, stdout, stderr = ssh.exec_command(run_cmd, timeout=5)
pid_output = stdout.read().decode().strip()
print(f"[monitor] started: {pid_output}")

start = time.time()
detected = False
last_size = 0

try:
    with ssh.open_sftp() as sftp:
        while time.time() - start < timeout and not detected:
            time.sleep(2)
            try:
                stat = sftp.stat(outfile)
                if stat.st_size > last_size:
                    with sftp.open(outfile) as f:
                        f.seek(max(0, stat.st_size - 2048))
                        new_data = f.read().decode('utf-8', errors='replace')
                    for line in new_data.split('\n'):
                        line_lower = line.lower()
                        for kw in filter_keywords:
                            if kw.lower() in line_lower:
                                print(f">>> {line.strip()}")
                                detected = True
                                break
                    last_size = stat.st_size
            except:
                pass

            # Also check MQTT events directly
            if not detected:
                stdin2, stdout2, stderr2 = ssh.exec_command(
                    f'mosquitto_sub -h localhost -p 1883 -u mqtt -P CHANGE_ME '
                    f'-t zigbee2mqtt/bridge/event -C 1 -W 2 -v 2>&1', timeout=5)
                event_out = stdout2.read().decode().strip()
                if event_out and 'error' not in event_out.lower():
                    print(f"[MQTT event] {event_out}")
                    detected = True

finally:
    # Cleanup: kill background process and remove file
    ssh.exec_command(f'kill $(cat {outfile}.pid 2>/dev/null) 2>/dev/null; rm -f {outfile}', timeout=5)
    ssh.close()

if detected:
    print("\n=== DEVICE DETECTED ===")
else:
    print("\n=== No device detected within timeout ===")
