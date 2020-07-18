//vault write sys/policy/pbb rules=@pbb.hcl
//vault token-create -period=10000h -policy=pbb
//Key                  Value
//---                  -----
//token                71c3f31f-39fb-b9fc-db42-e7c55ecda6f4
//token_accessor       3fa953ba-2251-eba5-25c9-35f0fee3b788
//token_duration       10000h
//token_renewable      true
//token_policies       ["default" "pbb"]
//identity_policies    []
//policies             ["default" "pbb"]

path "secret/mg" {
  capabilities = ["read"]
}

path "secret/bb" {
  capabilities = ["read"]
}
//private_key=zopsgithubot....???

path "secret/postgres" {
  capabilities = ["read"]
}
//username=bb_zops
//password=Eng5rie4Ach5ooghkei9xeeMiWee0Eex

path "secret/bbwww" {
  capabilities = ["read"]
}
//name=bbzops
//pw=Nahnai0OThu9tei6

path "zbb/*" {
  capabilities = ["read"]
}

// TODO: haproxy user and pw
//zops-bb
//IeZo7eesdeGieph5IoY1Zu7TAth0Xeew