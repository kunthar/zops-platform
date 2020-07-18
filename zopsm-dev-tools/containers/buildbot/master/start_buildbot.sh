#!/usr/bin/env sh

# startup script for purely stateless master

# we download the config from an arbitrary curl accessible tar.gz file (which github can generate for us)

B=/var/lib/buildbot

# copy the default buildbot.tac and master.cfg if not provided by the config
if [ ! -f $B/buildbot.tac ]
then
    echo "You didn't provide buildbot.tac"
    exit 1
fi

if [ ! -f $B/master.cfg ]
then
    echo "You didn't provide master.cfg"
    exit 1
fi

# Fixed buildbot master not start error in docker
rm -f $B/twistd.pid

# wait for db to start by trying to upgrade the master
until buildbot upgrade-master $B
do
    echo "Can't upgrade master yet. Waiting for database ready?"
    sleep 1
done

# we use exec so that twistd use the pid 1 of the container, and so that signals are properly forwarded
exec twistd -ny $B/buildbot.tac