#!/bin/bash

#export VAULT_TOKEN=s.gDEWzyvOjTChHu5ynC43nAY7
#export VAULT_SKIP_VERIFY=true
#export VAULT_ADDR=http://192.168.50.101:8200

export VAULT_TOKEN=s.gDEWzyvOjTChHu5ynC43nAY7
export VAULT_SKIP_VERIFY=true
export VAULT_ADDR=http://192.168.50.101:8200
python3 -m vaultbrowser.main
