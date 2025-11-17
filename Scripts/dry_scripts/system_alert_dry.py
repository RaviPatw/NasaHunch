#!/usr/bin/env python3
import time
import random
import psutil

THRESHOLDS = {
    "cpu": 90,
    "memory": 90,
    "disk": 90
}

CHECK_INTERVAL = 5   # Short for testing (instead of 300 seconds)

def fake_email(subject, body):
    """Simulate email sending without SMTP."""
    print("\n===== [SIMULATED EMAIL ALERT] =====")
    print("Subject:", subject)
    print("Body:\n" + body)
    print("===================================\n")

def get_metric(metric_name, real_value):
    """
    Return the real metric OR a simulated one
    to test alerts (random spikes).
    """
    # 70% chance to return real values
    if random.random() < 0.7:
        return real_value

    # 30% chance to simulate a spike
    if metric_name == "cpu":
        return random.randint(10, 100)
    if metric_name == "memory":
        return random.randint(20, 100)
    if metric_name == "disk":
        return random.randint(50, 100)

def main():
    print("🔔 Starting System Alert Monitor (DRY RUN MODE)...")
    print("Alerts will print instead of sending real emails.\n")

    while True:
        cpu_real = psutil.cpu_percent()
        mem_real = psutil.virtual_memory().percent
        disk_real = psutil.disk_usage("/").percent

        # Simulated OR real values
        cpu = get_metric("cpu", cpu_real)
        mem = get_metric("memory", mem_real)
        disk = get_metric("disk", disk_real)

        alerts = []
        if cpu > THRESHOLDS["cpu"]:
            alerts.append(f"High CPU usage: {cpu}%")
        if mem > THRESHOLDS["memory"]:
            alerts.append(f"High memory usage: {mem}%")
        if disk > THRESHOLDS["disk"]:
            alerts.append(f"High disk usage: {disk}%")

        print(f"[Metrics] CPU={cpu}%  MEM={mem}%  DISK={disk}%")

        if alerts:
            body = "\n".join(alerts)
            fake_email("🚨 Raspberry Pi Alert (DRY RUN)", body)

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
