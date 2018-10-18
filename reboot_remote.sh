#!/bin/bash

. ./config.sh

eval "{ sleep 1;
        echo $USER;
        sleep 1;
        echo $PASSWORD;
        sleep 1;
        printf 'import machine; machine.reset()\r\n'
        sleep 1;
    }" | telnet $BOTSHOST