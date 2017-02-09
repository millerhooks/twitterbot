#!/bin/bash

./build/scripts/style_bash_message.sh "Setup Nginx."

# enable nginx
rm -f /etc/service/nginx/down

# Set up nginx
rm /etc/nginx/sites-enabled/default
cp /build/deploy/nginx/webapp.conf /etc/nginx/sites-enabled/webapp.conf
cp /build/deploy/nginx/nginx.conf /etc/nginx/nginx.conf
