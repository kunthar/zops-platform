#!/bin/sh

/entrypoint.sh
sleep 15
/initialize.sh
tail -f /dev/null