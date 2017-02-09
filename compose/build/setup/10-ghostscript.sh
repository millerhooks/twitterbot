#!/bin/sh

./build/scripts/style_bash_message.sh "Bootstrap Ghostscript."

# Do a Ghostscript
mkdir -p /opt/ghostscript/sobin/ && mkdir -p /opt/ghostscript/gs/bin
cp /build/bin/ghostscript/gs /usr/bin/gs
cp /build/bin/ghostscript/gs /opt/ghostscript/gs/bin/gs
cp /build/bin/ghostscript/libgs.so /opt/ghostscript/sobin/libgs.so
cp /build/bin/ghostscript/libgs.so /usr/lib/libgs.so
cp -r /build/bin/ghostscript/Resource /opt/ghostscript/gs/Resource

mkdir -p /usr/local/share/ghostscript/
ln -s /opt/gsfonts /usr/local/share/ghostscript/fonts