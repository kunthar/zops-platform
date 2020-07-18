# -*-  coding: utf-8 -*-

from pushjack import APNSClient
from pushjack import GCMClient

from zopsm.lib.settings import VAULT_PUSH_APNS_PATH, VAULT_PUSH_FCM_PATH
from zopsm.lib.sd_vault import vault
import base64
import os

from zopsm.lib.log_handler import zlogger


def ios(tokens, val, project_id):
    """
    Sends push message to ios clients.
    
    Args:
        - tokens(list): client token list
        - val(dict): including title, body, type, language, icon, image, badge.
    
    """
    path = VAULT_PUSH_APNS_PATH.format(project_id=project_id)
    data = vault.read(path=path)['data']
    pem_file = data['cert_file']

    certificate_path = "{project_id}.pem".format(project_id=project_id)

    # todo: docker temp file best practices
    with open(certificate_path, "wb") as fh:
        fh.write(base64.b64decode(bytes(pem_file, 'utf-8')))

    os.chmod(certificate_path, 0o600)

    client = APNSClient(certificate=certificate_path,
                        default_error_timeout=10,
                        default_expiration_offset=2592000,
                        default_batch_size=100)

    message = val['body']

    # Options should increase according to parameters.
    options = {
        'title': val['title'],
        'launch_image': val['image'],
        'badge': val['badge'],
        'extra': val['extra']
    }

    # Send to multiple devices by passing a list of tokens.
    res = client.send(tokens, message, **options)
    client.close()
    os.remove(certificate_path)
    return res


def android(tokens, val, project_id):
    """
    Sends push message to android clients.

    Args:
        - tokens(list): client token list
        - val(dict): including title, body, type, language, icon, image, badge.

    """
    path = VAULT_PUSH_FCM_PATH.format(project_id=project_id)
    data = vault.read(path=path)['data']
    api_key = data['api_key']
    client = GCMClient(api_key=api_key)
    alert = val['extra']
    options = {
        'notification': {
            'title': val['title'],
            'body': val['body'],
            'sound': 'default',
            'color': "#009999",
            "icon": val['icon'] or 'default'
        },
        'collapse_key': 'collapse_key',
        'delay_while_idle': True,
        # todo push message time to live
        'time_to_live': 604800,
    }

    return client.send(tokens, alert, **options)

    # Alert can also be be a dictionary with data fields.
    # alert = {'message': 'Hello world', 'custom_field': 'Custom Data'}

    # List of successful registration ids.
    # res.successes

    # List of failed registration ids.
    # res.failures

    # detailed docs
    # https://github.com/dgilland/pushjack
    # https://pushjack.readthedocs.io/en/latest/


def send_push_message(service_type, tokens, val, project_id):
    """
    Sends push message to clients according to device service_type.

    Args:
        - tokens(list): client token list
        - val(dict): including title, body, service_type, language, icon, image, badge.

    """
    services = {'ios': ios,
                'android': android}

    try:

        res = services[service_type](tokens, val, project_id)
        zlogger.info("Push %s succces. project id: %s, success: %s",
                     service_type, project_id, res.successes)
        zlogger.error("Push %s result. project id: %s, failures: %s, errors: %s", service_type,
                      project_id, res.failures, res.errors)

    except Exception as e:
        zlogger.error("Unified push error: %s", str(e))
