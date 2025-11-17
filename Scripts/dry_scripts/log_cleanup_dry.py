#!/usr/bin/env python3
import os
import time
import gzip
import shutil
from datetime import datetime

LOG_DIR = "/var/log"
MAX_DAYS = 14
MAX_SIZE_MB = 50
DRY_RUN = True  # Set True for dry-run

def compress_file(file_path):
    if DRY_RUN:
        print(f"[DRY-RUN] Would compress large log: {file_path}")
    else:
        with open(file_path, "rb") as f_in:
            with gzip.open(file_path + ".gz", "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        os.remove(file_path)
        print(f"Compressed large log: {file_path}")

def cleanup_logs():
    cutoff = time.time() - (MAX_DAYS * 86400)
    for root, _, files in os.walk(LOG_DIR):
        for file in files:
            path = os.path.join(root, file)
            if file.endswith(".gz"):
                continue
            try:
                file_age = os.path.getmtime(path)
                file_size_mb = os.path.getsize(path) / 1_000_000

                if file_age < cutoff:
                    if DRY_RUN:
                        print(f"[DRY-RUN] Would delete old log: {path}")
                    else:
                        os.remove(path)
                        print(f"Deleted old log: {path}")

                elif file_size_mb > MAX_SIZE_MB:
                    compress_file(path)

            except Exception as e:
                print(f"[WARNING] Could not process {path}: {e}")

if __name__ == "__main__":
    print(f"[{datetime.now()}] Starting log cleanup (dry-run={DRY_RUN})...")
    cleanup_logs()
    print(f"[{datetime.now()}] Log cleanup complete (dry-run={DRY_RUN})")
