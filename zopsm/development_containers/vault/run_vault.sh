#!/bin/sh
/bin/vault server -dev -dev-root-token-id=$VAULT_DEV_ROOT_TOKEN_ID -dev-listen-address=$VAULT_DEV_LISTEN_ADDRESS
/bin/vault auth