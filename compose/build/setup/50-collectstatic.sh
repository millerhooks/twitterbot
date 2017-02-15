#!/bin/bash
./build/scripts/style_bash_message.sh "Collect Static Files, Deleting Brandly Sources"

if [ "$2" = "true" ]; then
    python3 /home/django/manage.py collectstatic --no-input
    chmod -R a+x /home/django/tiamat/public
fi