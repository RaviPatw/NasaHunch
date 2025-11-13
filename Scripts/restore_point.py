#!/usr/bin/env python3
import os
import subprocess
from datetime import datetime

SNAPSHOT_DIR = "/mnt/usb/snapshots"

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def create_snapshot():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    snapshot_path = os.path.join(SNAPSHOT_DIR, f"snapshot_{timestamp}")
    subprocess.run(["rsync", "-a", "--delete", "/", snapshot_path,
                    "--exclude=/proc", "--exclude=/sys", "--exclude=/tmp",
                    "--exclude=/mnt", "--exclude=/dev", "--exclude=/run"])
    print(f"Snapshot created at {snapshot_path}")

def list_snapshots():
    for s in os.listdir(SNAPSHOT_DIR):
        print(s)

def restore_snapshot(snapshot_name):
    snapshot_path = os.path.join(SNAPSHOT_DIR, snapshot_name)
    if not os.path.exists(snapshot_path):
        print("Snapshot not found.")
        return
    print(f"Restoring snapshot {snapshot_name}...")
    subprocess.run(["rsync", "-a", "--delete", snapshot_path + "/", "/"])

if __name__ == "__main__":
    ensure_dir(SNAPSHOT_DIR)
    create_snapshot()
