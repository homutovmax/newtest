#!/usr/bin/env python3
"""Diagnose and fix ChildProcess.kill issue with PowerShell in this environment."""
import subprocess, sys, os

def run(cmd):
    try:
        r = subprocess.run(
            ["powershell", "-NoLogo", "-NoProfile", "-NonInteractive", "-Command", cmd],
            capture_output=True, text=True, timeout=10,
        )
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", "TIMEOUT"
    except Exception as e:
        return -2, "", str(e)

print("=" * 55)
print("BASH DIAGNOSTIC")
print("=" * 55)

# 1. Simple echo test
rc, out, err = run("echo test")
print(f"1. echo test: rc={rc}, out={out!r}, err={err!r}")

# 2. Check for zombie powershell processes
rc, out, err = run("Get-Process powershell -ErrorAction SilentlyContinue | Format-Table Id, ProcessName, CPU, WorkingSet -AutoSize")
print(f"2. PowerShell processes:\n{out}")

# 3. Execution policy
rc, out, err = run("Get-ExecutionPolicy -Scope CurrentUser")
print(f"3. Execution policy (CurrentUser): {out}")
rc, out, err = run("Get-ExecutionPolicy -Scope LocalMachine")
print(f"4. Execution policy (LocalMachine): {out}")

# 4. Check if powershell.exe itself works
rc, out, err = run("$PSVersionTable.PSVersion")
print(f"5. PowerShell version: {out}")

# 5. Memory / CPU
rc, out, err = run("Get-Counter '\\Memory\\Available MBytes' -ErrorAction SilentlyContinue | Select-Object -ExpandProperty CounterSamples | Select-Object -ExpandProperty CookedValue")
print(f"6. Available memory (MB): {out}")

# 6. Environment info
rc, out, err = run("Get-ChildItem Env: | Where-Object { $_.Name -match 'PATH|TEMP|TMP|USER' } | Format-Table Name, Value -AutoSize")
print(f"7. Environment:\n{out}")

print("\nIf step 1 fails, the issue is systemic (antivirus/tool bug).")
print("If only later steps fail, there's a PowerShell config issue.")
print("Try: close this session, start a new one, run `echo test`.")
