#!/usr/bin/env python3
import subprocess
import json
import time
from datetime import datetime

SERVICES = ["nginx", "ssh", "docker", "prometheus-node-exporter"]
LOG_FILE = "/var/log/service_health.json"
INTERVAL = 300 

def check_service(service):
    cmd = ["systemctl", "is-active", service]
    try:
        output = subprocess.check_output(cmd, text=True).strip()
        return output == "active"
    except subprocess.CalledProcessError:
        return False

def log_status(status_dict):
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(status_dict) + "\n")

def main():
    while True:
        timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        status = {svc: check_service(svc) for svc in SERVICES}
        entry = {"time": timestamp, "status": status}
        print(entry)
        log_status(entry)
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
