#!/bin/sh
if [ -z "$1" ]; then
    echo "No server specified"
    exit 22
fi
echo "[FoxServers] Stopping ${1}..."
sudo docker-compose --file /opt/foxservers/core/docker-compose.yml --env-file /srv/foxservers/${1}/.foxservers-core.env down