#!/bin/bash
STRING=$1
PAD="%$((66 - ${#STRING}))s"
PAD=$(printf $PAD)
PAD=$(printf "%$((${#PAD} / 2))s")

echo -e "\n\033[1;33m\t\t######################################################################"

while read -r line; do
    echo -e "\t\t##$PAD\033[1;35m$line\033[1;33m$PAD##"
done <<< "$STRING"

echo -e "\t\t######################################################################\033[0m\n"