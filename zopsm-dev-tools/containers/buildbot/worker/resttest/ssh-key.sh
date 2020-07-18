#!/usr/bin/env bash

mkdir -p /home/buildbot/.ssh
touch /home/buildbot/.ssh/id_rsa
touch /home/buildbot/.ssh/known_hosts
#private_key=$(curl --header "X-Vault-Token: $VAULT_TOKEN" http://$VAULT_ADDR/v1/secret/bb | jq -r .data.private_key)
private_key=$(http https://${VAULT_NODE}:8200/v1/secret/bb X-Vault-Token:${VAULT_TOKEN} --cert=/home/buildbot/ssl/vault.cert --cert-key=/home/buildbot/ssl/vault.key --verify=/home/buildbot/ssl/ca.cert | jq -r .data.private_key)
echo "$private_key" > /home/buildbot/.ssh/id_rsa
chmod 0600 /home/buildbot/.ssh/id_rsa
ssh-keyscan -H github.com > /home/buildbot/.ssh/known_hosts
eval "$(ssh-agent -s)"
git clone git@github.com:kunthar/zopsm.git
