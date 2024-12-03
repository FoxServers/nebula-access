#!/bin/sh
if [ -z "$1" ]; then
    echo "No server specified"
    exit 22
fi
echo "[FoxServers] Starting ${1}..."
sudo docker-compose --file /srv/foxservers/${1}/docker-compose.yml --env-file /srv/foxservers/${1}/.foxservers-core.env up --detach