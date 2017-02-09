#!/bin/bash

# Fantastic apt caching
# https://gist.github.com/dergachev/8441335
# https://github.com/sameersbn/docker-apt-cacher-ng

./build/scripts/style_bash_message.sh "http://localhost:3142/acng-report.html for more details."

CONNECTION_STRING=$1
if [ $? -eq 0 ]; then
    echo "Acquire::HTTP::Proxy \"$CONNECTION_STRING\";" >> /etc/apt/apt.conf.d/01proxy
    echo 'Acquire::HTTPS::Proxy "false";' >> /etc/apt/apt.conf.d/01proxy

    ./build/scripts/style_bash_message.sh "Using host's apt proxy"

    ./build/scripts/style_bash_message.sh "$cat /etc/apt/apt.conf.d/01proxy"

    cat /etc/apt/apt.conf.d/01proxy
    echo ""
    ./build/scripts/style_bash_message.sh "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
else
    ./build/scripts/style_bash_message.sh "No apt proxy detected on Docker host"
fi