#!/bin/sh
if [ -d "/srv/foxservers/${1}" ]; then
    printf 'Server already initialized, would you like to override configuration (y/N)? '
    read answer
    if [ "$answer" != "${answer#[Yy]}" ] ;then 
        continue
    else
        exit
    fi
else
    sudo mkdir /srv/foxservers/${1}
fi

if [ -z "$1" ]; then
    echo "No output folder specified"
    exit 22
fi

if [ -z "$2" ]; then
    echo "No .env file specified"
    exit 22
fi
if ! [ -z "$2" ]; then
    if [ -d "${2}" ]; then
        echo "$2 should be .env, not directory";
        exit 21
    fi
    case $2 in
        --skip-env)
            continue
            ;;

        *)
            sudo mv ${2} /srv/foxservers/${1}/.foxservers-core.env
            ;;
    esac
fi

if [ -z "$3" ]; then
    echo "No dockerfile specified"
    exit 22
fi
if ! [ -z "$3" ]; then
    if [ -d "${3}" ]; then
        echo "$3 should be dockerfile, not directory";
        exit 21
    fi
    sudo mv ${3} /srv/foxservers/${1}/
fi

if ! [ -z "$4" ]; then
    if [ -d "${4}" ]; then
        echo "$4 should be .zip of mods, not directory";
        exit 21
    fi
    sudo mv ${4} /srv/foxservers/${1}/
fi

if ! [ -z "$5" ]; then
    if [ -d "${5}" ]; then
        echo "$5 should be .png, not directory";
        exit 21
    fi
    sudo mv ${5} /srv/foxservers/${1}/
fi