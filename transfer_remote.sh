#!/bin/bash

. ./config.sh

TARGET=/
SOURCE=$(pwd)/machine

lftp $USER:$PASSWORD@$BOTSHOST -e "
    mirror -R -v --no-perms --ignore-time --exclude --reverse --verbose $SOURCE $TARGET
"
