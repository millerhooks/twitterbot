#!/bin/sh

./build/scripts/style_bash_message.sh "Setup Python."

pip3 install pip --upgrade
pip3 install -r /home/django/requirements.txt