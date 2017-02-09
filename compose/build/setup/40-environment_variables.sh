#!/bin/sh
DEV=$2

if [ "$DEV" ]; then
    ./build/scripts/style_bash_message.sh "Skipping Env Var Setup for Dev"
else
    ./build/scripts/style_bash_message.sh "Run Env Vars Scripts"

    # Load Production Environment Vars
    cp -r /build/deploy/container_environment /etc/
    chmod 755 /etc/container_environment && chmod 644 /etc/container_environment.sh /etc/container_environment.json
fi