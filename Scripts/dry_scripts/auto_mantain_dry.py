#!/usr/bin/env python3
import subprocess
import time
import os
from datetime import datetime

LOG_FILE = "./auto_maintain_test.log"
BACKUP_FILE = "./etc_backup_test.tar.gz"
REBOOT_ON_KERNEL_UPDATE = True

SIMULATE = True


def log(message):
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    entry = f"{timestamp} {message}"
    print(entry)
    with open(LOG_FILE, "a") as f:
        f.write(entry + "\n")


def run(cmd):
    """Runs or simulates a command safely."""
    log(f"Running: {' '.join(cmd)}")

    if SIMULATE:
        log(f"[SIMULATED] Command would run: {' '.join(cmd)}")
        return 0, "[simulated output]"

    try:
        result = subprocess.run(cmd, text=True, capture_output=True)
        output = (result.stdout or "") + (result.stderr or "")
        log(output.strip())
        return result.returncode, output
    except Exception as e:
        log(f"ERROR executing command: {e}")
        return 1, str(e)


def backup_etc():
    """Simulate /etc backup."""
    log("Creating /etc backup...")
    cmd = ["tar", "-czf", BACKUP_FILE, "/etc"]
    code, _ = run(cmd)
    if code == 0:
        log(f"/etc backup saved to {BACKUP_FILE}")
    else:
        log("WARNING: /etc backup failed, continuing anyway.")


def update_package_lists():
    log("Updating package lists...")
    run(["apt-get", "update"])


def upgrade_packages():
    log("Upgrading packages...")
    code, output = run(["apt-get", "-y", "full-upgrade"])

    kernel_updated = "linux-image" in output or "linux-headers" in output
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
    log("===== AUTO MAINTENANCE STARTED (SAFE TEST MODE) =====")

    backup_etc()
    update_package_lists()
    kernel_updated = upgrade_packages()
    cleanup()

    if kernel_updated and REBOOT_ON_KERNEL_UPDATE:
        log("Kernel update detected; would reboot now.")
        time.sleep(2)
        reboot_system()
    else:
        log("No reboot required.")

    log("===== AUTO MAINTENANCE COMPLETED =====")


if __name__ == "__main__":
    main()
