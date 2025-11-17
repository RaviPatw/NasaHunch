#!/usr/bin/env python3
import os
import time
from datetime import datetime

SOURCE_DIRS = ["/home/pi/projects", "/etc", "/var/www"]
BACKUP_DIR = "/mnt/usb/backups"
RETENTION_DAYS = 14
DRY_RUN = True 

def ensure_dir(path):
    if DRY_RUN:
        print(f"[DRY-RUN] Would ensure directory exists: {path}")
    else:
        os.makedirs(path, exist_ok=True)

def create_backup():
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"backup_{timestamp}.tar.gz")
    cmd = ["tar", "-czf", backup_file] + SOURCE_DIRS

    if DRY_RUN:
        print(f"[DRY-RUN] Would run: {' '.join(cmd)}")
        print(f"[DRY-RUN] Backup would be saved to: {backup_file}")
    else:
        import subprocess
        subprocess.run(cmd)
        print(f"Backup saved to {backup_file}")

def cleanup_old_backups():
    cutoff = time.time() - RETENTION_DAYS * 86400
    for file in os.listdir(BACKUP_DIR):
        path = os.path.join(BACKUP_DIR, file)
        if os.path.getmtime(path) < cutoff:
            if DRY_RUN:
                print(f"[DRY-RUN] Would remove old backup: {path}")
            else:
                os.remove(path)
                print(f"Removed old backup: {path}")

def main():
    ensure_dir(BACKUP_DIR)
    create_backup()
    cleanup_old_backups()

if __name__ == "__main__":
    main()








#####################################################################################
#### Fix [DRY-RUN] Would ensure directory exists: /mnt/usb/backups
# /mnt/c/Users/ravip/Downloads/NasaHunch/Scripts/backup_data_dry.py:18: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
#   timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
# [DRY-RUN] Would run: tar -czf /mnt/usb/backups/backup_20251113_194633.tar.gz /home/pi/projects /etc /var/www
# [DRY-RUN] Backup would be saved to: /mnt/usb/backups/backup_20251113_194633.tar.gz
# Traceback (most recent call last):
#   File "/mnt/c/Users/ravip/Downloads/NasaHunch/Scripts/backup_data_dry.py", line 47, in <module>
#     main()
#   File "/mnt/c/Users/ravip/Downloads/NasaHunch/Scripts/backup_data_dry.py", line 44, in main
#     cleanup_old_backups()
#   File "/mnt/c/Users/ravip/Downloads/NasaHunch/Scripts/backup_data_dry.py", line 32, in cleanup_old_backups
#     for file in os.listdir(BACKUP_DIR):
#                 ^^^^^^^^^^^^^^^^^^^^^^
# FileNotFoundError: [Errno 2] No such file or directory: '/mnt/usb/backups'
#######################################################################################