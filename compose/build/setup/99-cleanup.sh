#!/bin/sh

./build/scripts/style_bash_message.sh "Cleanup."

# Drop the apt-proxy
echo "" > /etc/apt/apt.conf.d/01proxy