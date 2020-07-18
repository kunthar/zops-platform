#!/usr/bin/env bash
set -x

c=("zopsm-base" "auth" "logger" "saas" "push" "mda" "zgateway" "zmta" "riak" "vault" "redis")



for i in ${c[@]}
do
    cd ../$i
    if [[ -f zopsm/development_containers/$i/entrypoint.sh ]]
    then
      cp zopsm/development_containers/$i/entrypoint.sh .
    fi
    if [[ $i == "zopsm-base" ]]
    then
      docker build --no-cache -t zetaops/zopsm-base .
    elif [[ $i == "zgateway" ]]
    then
      docker build --no-cache -t zetaops/zopsm-roc .
    elif [[ $i == "zmta" ]]
    then
      docker build --no-cache -t zetaops/zopsm-workers .
    elif [[ $i == "riak" ]]
    then
      cp -r zopsm/development_containers/$i/riak-rabbitmq-commit-hooks .
      docker build --no-cache -t zetaops/zopsm-riak .
    else
      docker build --no-cache -t zetaops/zopsm-$i .
    fi
done

set +x
