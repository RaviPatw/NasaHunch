#!/usr/bin/env python3
import os
import shutil
from datetime import datetime

# Use local directory instead of /mnt/usb/snapshots
SNAPSHOT_DIR = "./snapshots_test"
TEST_SOURCE_DIR = "./fake_root"  

EXCLUDES = ["proc", "sys", "tmp", "mnt", "dev", "run"]


def ensure_dirs():
    os.makedirs(SNAPSHOT_DIR, exist_ok=True)
    os.makedirs(TEST_SOURCE_DIR, exist_ok=True)

    # Create some fake files if empty
    if not os.listdir(TEST_SOURCE_DIR):
        with open(os.path.join(TEST_SOURCE_DIR, "etc_config.txt"), "w") as f:
            f.write("system config example")
        with open(os.path.join(TEST_SOURCE_DIR, "home_user_file.txt"), "w") as f:
            f.write("user data example")


def create_snapshot():
    """Simulate a snapshot by copying a fake filesystem directory."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    snapshot_path = os.path.join(SNAPSHOT_DIR, f"snapshot_{timestamp}")

    print(f"Creating dry-run snapshot: {snapshot_path}")

    shutil.copytree(
        TEST_SOURCE_DIR,
        snapshot_path,
        ignore=shutil.ignore_patterns(*EXCLUDES)
    )

    print(f"Snapshot created at {snapshot_path}")


def list_snapshots():
    print("\nAvailable snapshots:")
    for entry in os.listdir(SNAPSHOT_DIR):
        print(" -", entry)


def restore_snapshot(name):
    """Simulate restoring a snapshot into fake_root/."""
    snapshot_path = os.path.join(SNAPSHOT_DIR, name)

    if not os.path.exists(snapshot_path):
        print("Snapshot not found.")
        return

    print(f"\nRestoring snapshot {name} → {TEST_SOURCE_DIR}")

    # Delete old fake_root contents
    for item in os.listdir(TEST_SOURCE_DIR):
        path = os.path.join(TEST_SOURCE_DIR, item)
        if os.path.isfile(path):
            os.remove(path)
        else:
            shutil.rmtree(path)

    # Copy snapshot data back
    for item in os.listdir(snapshot_path):
        src = os.path.join(snapshot_path, item)
        dst = os.path.join(TEST_SOURCE_DIR, item)

        if os.path.isfile(src):
            shutil.copy2(src, dst)
        else:
            shutil.copytree(src, dst)

    print("Restore complete (dry-run).")


if __name__ == "__main__":
    ensure_dirs()
    create_snapshot()
    list_snapshots()
    # Example restore (comment out if not needed)
    # restore_snapshot("snapshot_20251117_1400")
