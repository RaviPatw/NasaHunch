#!/usr/bin/env python3
import subprocess
import time
import os
from datetime import datetime

LOG_FILE = "/var/log/auto_maintain.log"
REBOOT_ON_KERNEL_UPDATE = True
BACKUP_FILE = "/var/backups/etc_backup.tar.gz"


def log(message):
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    entry = f"{timestamp} {message}"
    print(entry)
    with open(LOG_FILE, "a") as f:
        f.write(entry + "\n")


def run(cmd):
    """
    Runs a command and returns output.
    If error occurs, returns output anyway.
    """
    log(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd,
            text=True,
            capture_output=True
        )
        output = (result.stdout or "") + (result.stderr or "")
        log(output.strip())
        return result.returncode, output
    except Exception as e:
        log(f"ERROR executing command: {e}")
        return 1, str(e)


def backup_etc():
    """
    Creates a quick /etc backup in case an upgrade breaks config files.
    """
    log("Creating /etc backup...")
    try:
        cmd = ["tar", "-czf", BACKUP_FILE, "/etc"]
        code, out = run(cmd)
        if code == 0:
            log(f"/etc backup saved to {BACKUP_FILE}")
        else:
            log("WARNING: /etc backup failed, continuing anyway.")
    except Exception as e:
        log(f"Backup failed: {e}")


def update_package_lists():
    log("Updating package lists...")
    code, _ = run(["apt-get", "update"])
    if code != 0:
        log("ERROR: apt-get update failed.")


def upgrade_packages():
    log("Upgrading packages...")
    code, output = run(["apt-get", "-y", "full-upgrade"])

    kernel_updated = False
    for line in output.splitlines():
        if "linux-image" in line or "linux-headers" in line:
            kernel_updated = True

    return kernel_updated


def cleanup():
    log("Cleaning up unused packages...")
    run(["apt-get", "-y", "autoremove"])
    run(["apt-get", "autoclean"])


def reboot_system():
    log("Rebooting system due to kernel update...")
    run(["systemctl", "reboot"])


def ensure_log_file():
    try:
        open(LOG_FILE, "a").close()
    except Exception:
        pass


def main():
    ensure_log_file()
    log("===== AUTO MAINTENANCE STARTED =====")

    backup_etc()
    update_package_lists()
    kernel_updated = upgrade_packages()
    cleanup()

    if kernel_updated and REBOOT_ON_KERNEL_UPDATE:
        log("Kernel update detected; reboot required.")
        time.sleep(5)  
        reboot_system()
    else:
        log("No reboot required.")

    log("===== AUTO MAINTENANCE COMPLETED =====")


if __name__ == "__main__":
    while True:
        main()
        time.sleep(86400)
