#!/usr/bin/env python3
import os, subprocess, psutil, time, json
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

PUSHGATEWAY_URL = "http://localhost:9091"  # use localhost for testing
NODE_NAME = os.uname()[1]
REPORT_FILE = f"./maintenance_{NODE_NAME}.json"  # local path for non-root test

registry = CollectorRegistry()
cpu_temp = Gauge('cpu_temperature_celsius', 'CPU temperature', registry=registry)
cpu_usage = Gauge('cpu_usage_percent', 'CPU usage', registry=registry)
mem_usage = Gauge('memory_usage_percent', 'Memory usage', registry=registry)
disk_usage = Gauge('disk_usage_percent', 'Disk usage', registry=registry)
uptime_metric = Gauge('system_uptime_seconds', 'System uptime', registry=registry)

def get_cpu_temp():
    # Mock CPU temp if vcgencmd missing
    try:
        out = subprocess.check_output(['vcgencmd', 'measure_temp']).decode()
        return float(out.replace("temp=","").replace("'C\n",""))
    except Exception:
        temps = psutil.sensors_temperatures()
        if temps:
            for _, entries in temps.items():
                if entries: 
                    return entries[0].current
        return 45.0  # fallback fake temp

def get_uptime():
    return time.time() - psutil.boot_time()

def get_smart_status():
    try:
        out = subprocess.check_output(["smartctl", "-H", "/dev/sda"]).decode()
        if "PASSED" not in out:
            return "WARNING"
    except Exception:
        return "UNKNOWN"
    return "OK"

def main():
    data = {
        "node": NODE_NAME,
        "time": time.ctime(),
        "cpu_temp": get_cpu_temp(),
        "cpu_usage": psutil.cpu_percent(),
        "mem_usage": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage('/').percent,
        "uptime": get_uptime(),
        "smart_status": get_smart_status()
    }

    with open(REPORT_FILE, "a") as f:
        f.write(json.dumps(data) + "\n")

    cpu_temp.set(data["cpu_temp"])
    cpu_usage.set(data["cpu_usage"])
    mem_usage.set(data["mem_usage"])
    disk_usage.set(data["disk_usage"])
    uptime_metric.set(data["uptime"])

    # Comment out Pushgateway call if you don't have one running
    # push_to_gateway(PUSHGATEWAY_URL, job='raspi_maintenance', registry=registry)
    print(json.dumps(data, indent=2))

if __name__ == "__main__":
    main()
