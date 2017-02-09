#!/bin/bash

./build/scripts/style_bash_message.sh "Setup Poppler."

cd /build/deploy/deb && dpkg -i poppler_0.45.0-1_amd64.deb