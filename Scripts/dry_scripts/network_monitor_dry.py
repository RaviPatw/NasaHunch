#!/usr/bin/env python3
import subprocess
import time
import socket
import json
import os
from datetime import datetime

# Write log to local folder instead of /var/log
LOG_FILE = "./network_monitor_testlog.json"
CHECK_INTERVAL = 5      # Lower interval for testing
TARGETS = ["8.8.8.8", "1.1.1.1", "google.com", "github.com"]
LATENCY_THRESHOLD_MS = 150


def log(data):
    """Append JSON entry to the log file."""
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(data) + "\n")


def ping_target(target):
    """Ping a single host and return latency in ms or None if failed."""
    try:
        # Windows uses different ping flags → detect OS
        if os.name == "nt":
            # -n 1 : send 1 ping
            # -w 2000 : 2s timeout
            cmd = ["ping", "-n", "1", "-w", "2000", target]
        else:
            # Linux/macOS
            cmd = ["ping", "-c", "1", "-W", "2", target]

        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode != 0:
            return None

        # Look for time=XX ms in output
        for line in result.stdout.splitlines():
            if "time=" in line:
                value = line.split("time=")[1].split(" ")[0]
                return float(value.replace("ms", ""))

        return None

    except Exception:
        # If ping doesn't work at all (Windows without admin), fake a latency
        return 50.0


def dns_check(hostname="google.com"):
    """Test if DNS resolution works."""
    try:
        socket.gethostbyname(hostname)
        return True
    except Exception:
        return False


def main():
    print("🌐 Starting Network Monitor (DRY RUN)...")
    print(f"Logging to: {LOG_FILE}\n")

    while True:
        timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        results = {}

        for target in TARGETS:
            latency = ping_target(target)
            results[target] = {
                "status": "UP" if latency is not None else "DOWN",
                "latency_ms": latency
            }

        dns_ok = dns_check()

        alerts = []
        for t, info in results.items():
            if info["status"] == "DOWN":
                alerts.append(f"{t} unreachable")
            elif info["latency_ms"] and info["latency_ms"] > LATENCY_THRESHOLD_MS:
                alerts.append(f"{t} latency high ({info['latency_ms']} ms)")

        if not dns_ok:
            alerts.append("DNS resolution failed")

        status = {
            "time": timestamp,
            "results": results,
            "dns_ok": dns_ok,
            "alerts": alerts,
        }

        log(status)
        print(json.dumps(status, indent=2))
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
