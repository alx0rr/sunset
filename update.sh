#!/bin/bash

IMAGE="ghcr.io/alx0rr/sunset:latest"
INTERVAL=60

docker compose up -d
echo "Watching for updates..."

while true; do
    OLD=$(docker inspect --format='{{.Id}}' $IMAGE 2>/dev/null)
    
    if docker pull $IMAGE > /dev/null 2>&1; then
        NEW=$(docker inspect --format='{{.Id}}' $IMAGE)
        
        if [ "$OLD" != "$NEW" ]; then
            echo "[$(date)] New version found, restarting..."
            docker compose down
            docker compose up -d
            echo "[$(date)] Done!"
        else
            echo "[$(date)] Already up to date."
        fi
    else
        echo "[$(date)] Pull failed, skipping."
    fi
    
    sleep $INTERVAL
done