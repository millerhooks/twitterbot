#!/bin/sh
xargs -a <(awk '/^\s*[^#]/' /home/django/requirements.apt) -r -- apt-get -yq install