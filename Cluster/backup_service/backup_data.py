#!/usr/bin/env python3
import subprocess
import os
import time
from datetime import datetime, UTC

SOURCE_DIRS = ["/home/pi/projects", "/etc", "/var/www"]
# Matches the Docker volume mount in Cluster/docker-stack.yml
BACKUP_DIR = "/mnt/backup"
RETENTION_DAYS = 14

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def create_backup():
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"backup_{timestamp}.tar.gz")
    existing_sources = [path for path in SOURCE_DIRS if os.path.exists(path)]
    if not existing_sources:
        print("No source directories found; skipping backup.")
        return
    cmd = ["tar", "-czf", backup_file] + existing_sources
    subprocess.run(cmd, check=True)
    print(f"Backup saved to {backup_file}")

def cleanup_old_backups():
    cutoff = time.time() - RETENTION_DAYS * 86400
    if not os.path.isdir(BACKUP_DIR):
        return
    for file in os.listdir(BACKUP_DIR):
        path = os.path.join(BACKUP_DIR, file)
        if os.path.isfile(path) and os.path.getmtime(path) < cutoff:
            os.remove(path)
            print(f"Removed old backup: {path}")

def main():
    ensure_dir(BACKUP_DIR)
    create_backup()
    cleanup_old_backups()

if __name__ == "__main__":
    while True:
        main()
        time.sleep(86400)
