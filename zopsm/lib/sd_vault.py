from zopsm.lib.sd_consul import consul_client
import hvac
import os
import logging

token = os.getenv("VAULT_DEV_TOKEN")
req_id, vaults = consul_client.health.checks(service='vault')
passing_and_active_vault = ["{}.vault".format(v['Node']) for v in vaults if
                                (v['Status'] == 'passing' and v['ServiceTags'] == ['active'])]
try:
    vault = hvac.Client(url='https://{}:8200'.format(passing_and_active_vault[0]),
                        token=token, verify='/usr/local/share/ca-certificates/ca.cert',
                        cert=('/usr/local/share/ca-certificates/vault.cert',
                              '/usr/local/share/ca-certificates/vault.key'))
    vault.is_authenticated()
except OSError:
    vault = hvac.Client(url='http://vault:8200', token=token)
except Exception as e:
    logging.error("Error occured: {}".format(str(e)))
