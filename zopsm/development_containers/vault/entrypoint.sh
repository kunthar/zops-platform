#!/usr/bin/expect -f
spawn /run_vault.sh
set token "b258f5f2-fc67-24fe-3750-0055f625aa74\n"
sleep 10
expect "Token (will be hidden): "
send "$token\n"