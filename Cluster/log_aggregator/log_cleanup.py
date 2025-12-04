#!/usr/bin/env python3
import os
import time
import gzip
import shutil
from datetime import datetime, timedelta

LOG_DIR = "/var/log"
MAX_DAYS = 14
MAX_SIZE_MB = 50

def compress_file(file_path):
    with open(file_path, "rb") as f_in:
        with gzip.open(file_path + ".gz", "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
    os.remove(file_path)

def cleanup_logs():
    cutoff = time.time() - (MAX_DAYS * 86400)
    for root, _, files in os.walk(LOG_DIR):
        for file in files:
            path = os.path.join(root, file)
            if file.endswith(".gz"):
                continue
            try:
                if os.path.getmtime(path) < cutoff:
                    print(f"Deleting old log: {path}")
                    os.remove(path)
                elif os.path.getsize(path) / 1_000_000 > MAX_SIZE_MB:
                    print(f"Compressing large log: {path}")
                    compress_file(path)
            except Exception:
                pass

if __name__ == "__main__":
    while True:
        print(f"[{datetime.now()}] Starting log cleanup...")
        cleanup_logs()
        print("Cleanup complete.")
        time.sleep(86400)
