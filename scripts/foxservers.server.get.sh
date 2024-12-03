#!/bin/sh
case $1 in
    releases)
        curl -L "https://api.github.com/repos/FoxServers/docker/releases" | grep "tag_name"
        ;;
    *)
        if [ -d "/tmp/foxservers/downloads/"]
        then
            continue
        else
            sudo mkdir /tmp/foxservers/downloads/
        fi

        curl -L https://api.github.com/repos/FoxServers/docker/tarball/${1} -o ${1}.tar.gz
        sudo tar -zvxf ${1}.tar.gz --directory /tmp/foxservers/downloads --strip-components=1
        sudo mv /tmp/foxservers/downloads/docker-compose.yml ./
        sudo rm $1.tar.gz
        sudo rm -rf /tmp/foxservers/downloads/{*,.*}
        ;;

esac