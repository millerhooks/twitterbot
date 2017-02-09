#!/bin/sh

./build/scripts/style_bash_message.sh "Setup Runit Scripts."

# add some services for runit launcher
cp -r /build/deploy/service/postfix /etc/service/postfix

rm /etc/service/postfix/down
