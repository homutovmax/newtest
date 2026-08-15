#!python3
"""Run regression tests, then deploy cover formatting fix to server via paramiko."""
import subprocess, sys, os

# Step 1: Run regression tests
print("=" * 55)
print("  STEP 1: Running regression tests...")
print("=" * 55)
result = subprocess.run(
    [sys.executable, os.path.join(os.path.dirname(__file__), "run_tests.py")],
    capture_output=True, text=True, cwd=os.path.dirname(__file__),
)
print(result.stdout)
if result.returncode != 0:
    print("  REGRESSION TESTS FAILED — aborting deploy")
    print(result.stderr)
    sys.exit(1)
print("  All tests passed — proceeding with deploy")
print()

# Step 2: Deploy to server
import paramiko

HOST = "100.112.4.123"
PORT = 22
USER = "root"
PASSWORD = "CHANGE_ME"
REMOTE_APP = "/opt/hr/web/app.py"
REMOTE_MIGRATION = "/opt/hr/src/migration.py"

LOCAL_APP = os.path.join(os.path.dirname(__file__), "web", "app.py")
LOCAL_MIGRATION = os.path.join(os.path.dirname(__file__), "src", "migration.py")

print("=" * 55)
print("  STEP 2: Deploying to server...")
print("=" * 55)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    ssh.connect(HOST, PORT, USER, PASSWORD, timeout=15)
    sftp = ssh.open_sftp()

    print(f"  Uploading web/app.py → {REMOTE_APP}")
    sftp.put(LOCAL_APP, REMOTE_APP)

    print(f"  Uploading src/migration.py → {REMOTE_MIGRATION}")
    sftp.put(LOCAL_MIGRATION, REMOTE_MIGRATION)

    sftp.close()

    print("  Restarting container...")
    _, stdout, stderr = ssh.exec_command("docker restart hr-web-1")
    print(f"  {stdout.read().decode().strip()}")
    err = stderr.read().decode().strip()
    if err:
        print(f"  STDERR: {err}")

    print("  Done! http://100.112.4.123:8000/report")
except Exception as e:
    print(f"  ERROR: {e}")
    sys.exit(1)
finally:
    ssh.close()
