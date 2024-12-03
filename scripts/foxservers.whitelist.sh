#!/bin/sh
while true; do
    sudo /opt/foxservers/.venv/bin/python /opt/foxservers/core/whitelist/pull_whitelists.py
    sleep 10
done