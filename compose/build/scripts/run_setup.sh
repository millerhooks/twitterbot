#!/bin/bash
CONNECTION_STRING=$1
DEV=$2

chmod +x /build/setup/*

for SCRIPT in /build/setup/*
	do
		if [ -f $SCRIPT -a -x $SCRIPT ]
		then
		    echo $SCRIPT
            sleep 1
			$SCRIPT $CONNECTION_STRING $DEV
		fi
	done
