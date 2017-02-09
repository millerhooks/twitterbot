#!/bin/bash

bash /build/scripts/style_bash_message.sh "Install sfnt2woff, ttf2eot, ttfautohint, ttfautohitGUI"

cp /build/bin/font2css/* /usr/bin
cp -r /build/scripts/css3font/* /usr/bin