#!/usr/bin/env python3
import subprocess
import json
import time
import os
from datetime import datetime

SERVICES = ["nginx", "ssh", "docker", "prometheus-node-exporter"]

# Use local file instead of /var/log
LOG_FILE = "./service_health_test.json"

# Shorter interval for testing
INTERVAL = 5  # seconds


def check_service(service):
    """
    Try to check a service with systemctl.
    If systemctl fails (service not installed, permissions, etc)
    return a simulated state.
    """
    cmd = ["systemctl", "is-active", service]
    try:
        output = subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT).strip()
        return output == "active"

    except Exception:
        # Simulate service status: pretend half are active, half inactive
        simulated = hash(service) % 2 == 0
        return simulated


def log_status(status_dict):
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(status_dict) + "\n")


def main():
    print("🩺 Starting Service Health Monitor (DRY RUN)...")
    print(f"Logging to: {LOG_FILE}\n")

    while True:
        timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        status = {svc: check_service(svc) for svc in SERVICES}

        entry = {
            "time": timestamp,
            "status": status
        }

        print(json.dumps(entry, indent=2))
        log_status(entry)

        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
