#!/bin/bash
CONNECTION_STRING=$1

./build/scripts/style_bash_message.sh "Setup Additional PPA Repositories."
apt-add-repository ppa:inkscape.dev/stable

./build/scripts/style_bash_message.sh "Set up apt proxy so we can speed up future apt installs."
bash /build/scripts/detect_apt_proxy.sh ${CONNECTION_STRING}
apt-get update

./build/scripts/style_bash_message.sh "Install Apt Dependencies"
bash /build/scripts/get_apt_deps.sh

MAILER_TYPE=Brandly
URL=www.brandly.com

./build/scripts/style_bash_message.sh "Installing Postfix for $MAILER_TYPE | $URL"

debconf-set-selections <<< "postfix postfix/mailname string $URL"
debconf-set-selections <<< "postfix postfix/main_mailer_type string '$MAILER_TYPE'"
apt-get install -yq postfix
postconf compatibility_level=2

apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
