#!/usr/bin/env bash
touch /home/buildbot/.ssh/known_hosts
ssh-keyscan -H github.com > /home/buildbot/.ssh/known_hosts
eval "$(ssh-agent -s)"
git clone git@github.com:kunthar/zopsm-dev-tools.git
git clone git@github.com:kunthar/zopsm.git
echo "Host 159.69.*.*
  UserKnownHostsFile /dev/null
  StrictHostKeyChecking no" >> /home/buildbot/.ssh/config

