#!/bin/bash

. ./config.sh

TARGET=/flash
SOURCE=.

lftp $USER:$PASSWORD@$BOTSHOST -e "
    mirror -v --no-perms --ignore-time --exclude .git/ --reverse --delete --verbose $SOURCE $TARGET
"
