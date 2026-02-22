#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
QUEUE_DIR="$REPO_ROOT/queue"

echo "[1/3] Dry-run validation for queued contracts..."
python3 "$SCRIPT_DIR/deployer.py" --queue-dir "$QUEUE_DIR" --dry-run

echo "[2/3] Deploying queued contracts..."
python3 "$SCRIPT_DIR/deployer.py" --queue-dir "$QUEUE_DIR"

echo "[3/3] Listing services..."
docker service ls

echo "Hosting test complete."
