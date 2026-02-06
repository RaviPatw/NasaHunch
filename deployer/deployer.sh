#!/bin/bash
# NASA HUNCH Generic Application Deployer
# Runs on Raspberry Pi Linux
# Uses Docker Swarm to deploy unknown applications

set -e

QUEUE_DIR="../queue"

# Check if queue exists
if [ ! -d "$QUEUE_DIR" ]; then
  echo "Queue directory not found."
  exit 1
fi

# Get first app in queue
APP_FILE=$(ls "$QUEUE_DIR"/*.yaml 2>/dev/null | head -n 1)

if [ -z "$APP_FILE" ]; then
  echo "No applications waiting to deploy."
  exit 0
fi

echo "Found application contract: $APP_FILE"

# Parse YAML contract
NAME=$(yq e '.name' "$APP_FILE")
IMAGE=$(yq e '.image' "$APP_FILE")
TYPE=$(yq e '.type' "$APP_FILE")
PORT=$(yq e '.port' "$APP_FILE")
REPLICAS=$(yq e '.replicas' "$APP_FILE")

# Decide node placement
if [ "$TYPE" = "ai" ]; then
  CONSTRAINT="node.labels.role==ai"
else
  CONSTRAINT="node.labels.role==general"
fi

echo "Deploying application: $NAME"
echo "Image: $IMAGE"
echo "Type: $TYPE"

# Deploy service
docker service create \
  --name "$NAME" \
  --constraint "$CONSTRAINT" \
  --replicas "$REPLICAS" \
  --publish published=0,target="$PORT" \
  "$IMAGE"

# Remove from queue
rm "$APP_FILE"

echo "Deployment complete for $NAME"