#!/usr/bin/env python3
import smtplib
from email.mime.text import MIMEText
import psutil
import subprocess
import time

THRESHOLDS = {
    "cpu": 90,
    "memory": 90,
    "disk": 90
}
CHECK_INTERVAL = 300 
ALERT_EMAIL = "ravipatwardhan123@gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "your_email@example.com"
SMTP_PASS = "your_app_password"

def send_email(subject, body):
    msg = MIMEText(body)
    msg["From"] = SMTP_USER
    msg["To"] = ALERT_EMAIL
    msg["Subject"] = subject
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
    except Exception as e:
        print("Email failed:", e)

def main():
    while True:
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent
        disk = psutil.disk_usage("/").percent

        alerts = []
        if cpu > THRESHOLDS["cpu"]:
            alerts.append(f"High CPU usage: {cpu}%")
        if mem > THRESHOLDS["memory"]:
            alerts.append(f"High memory usage: {mem}%")
        if disk > THRESHOLDS["disk"]:
            alerts.append(f"High disk usage: {disk}%")

        if alerts:
            body = "\n".join(alerts)
            send_email("🚨 Raspberry Pi Alert", body)
            print("Alert sent:", body)

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
