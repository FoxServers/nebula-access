#!/bin/sh
if [ -z "$1" ]; then
    echo "No server specified"
    exit 22
fi
sudo /opt/foxservers/.venv/bin/python /opt/foxservers/core/server/add_server.py ${1}