import os
import json
from secrets import token_hex, token_urlsafe
from hashlib import sha512
from urllib import request
from urllib.parse import urlencode
from urllib.error import URLError
from datetime import datetime, timedelta
from jwt import encode, decode, ExpiredSignatureError, InvalidTokenError
from falcon.errors import HTTPInvalidParam, HTTPBadRequest, HTTPServiceUnavailable, HTTPFailedDependency
from zopsm.lib.settings import MAIL_GUN_API_KEY
from zopsm.lib.settings import MAIL_GUN_URL
from zopsm.lib.settings import ADDRESS_FROM
from zopsm.lib.settings import ZOPSM_APPROVE_URL, ZOPSM_FORGOT_PASSWORD_URL
from zopsm.lib.settings import APPROVE_CODE_MAIL_TEXT
from zopsm.lib.settings import APPROVE_CODE_MAIL_SUBJECT
from zopsm.lib.settings import RESET_PASSWORD_MAIL_TEXT
from zopsm.lib.settings import RESET_PASSWORD_MAIL_SUBJECT
from zopsm.lib.settings import CACHE_SERVICE_TOKEN_LIST, CACHE_TOKENS_KEYS,CACHE_REFRESH_TOKEN
from zopsm.lib.settings import CACHE_REFRESH_TOKEN_EXPIRE_IN
from zopsm.lib.settings import CACHE_SAAS_AUTH_TOKEN, PROJECT_SERVICES_ADMIN_TOKEN, ADMIN_TOKENS
from zopsm.lib.settings import CACHE_SAAS_RESET_PASSWORD_KEY
from zopsm.lib.utility import generate_uuid
from zopsm.lib.credis import ZRedis
from zopsm.lib.sd_redis import redis_db_pw
from zopsm.saas.log_handler import saas_logger

master = os.getenv('REDIS_HOST')

cache = ZRedis(host=master,
               password=redis_db_pw,
               db=os.getenv('REDIS_DB'))


def generate_token(lenght=32):
    return token_hex(lenght)


def generate_user_token(lenght=64):
    """
    Generates a urlsafe ascii default 40 byte length user auth token

    Args:
        lenght(int): length of token

    Returns: (str)

    """
    return token_urlsafe(lenght)


def create_auth_token_payload(user_id, role, tenant_id=None, account_id=None):
    iat = datetime.utcnow()
    exp = iat + timedelta(weeks=1)
    payload = {'exp': exp,
               'iat': iat,
               'sub': user_id,
               'rol': role.value,
               'tenant_id': tenant_id,
               'account_id': account_id}
    return payload


def create_reset_password_payload(email):
    iat = datetime.utcnow()
    exp = iat + timedelta(hours=2)
    payload = {'exp': exp,
               'iat': iat,
               'email': email}
    return payload


def encode_jwt_token(payload):
    """
    Encode JWT(JSON Web Token) token with payload. For information "https://pyjwt.readthedocs.io"
    Returns:
        str: Encoded JWT. Converted to STR
    """
    try:
        return encode(payload, os.environ.get('SECRET_KEY'), algorithm='HS256').decode()
    except Exception as e:
        return e


def decode_jwt_token(token, param):
    """
    Decode the jwt token

    :param token: decoded token
    :param param: for httpinvalidparam error
    :return: dict of payload
    """
    try:
        return decode(bytes(token.encode()), os.environ.get('SECRET_KEY'))
    except ExpiredSignatureError:
        raise HTTPInvalidParam(msg='Signature expired', param_name=param)

    except InvalidTokenError:
        raise HTTPInvalidParam(msg='Invalid token', param_name=param)


def init_zops_models(target_model):
    """
    Initialize given target_model class. Assign a uuid to _id attr.
    Args:
        target_model: Model class
    """
    target_model._id = generate_uuid()
    target_model.creation_time = datetime.utcnow()


def data_hashing(data):
    """
    Returns hashed value of `data`
    Args:
        data (str): String data.

    Returns:
        str: Hashed `data`
    """
    return sha512(data.encode()).hexdigest()


def send_reset_password_mail(email, token, testing_mode=False):
    url_data = urlencode({"token": token})
    mail_text = RESET_PASSWORD_MAIL_TEXT.format(url=ZOPSM_FORGOT_PASSWORD_URL, url_params=url_data)
    data = {
        "from": ADDRESS_FROM,
        "to": email,
        "subject": RESET_PASSWORD_MAIL_SUBJECT,
        "text": mail_text,
        "h:X-Reset-Token": token,
    }

    mail_id = send_mailgun(data, testing_mode)
    return {
        "id": mail_id,
        "text": mail_text,
        "subject": RESET_PASSWORD_MAIL_SUBJECT
    }


def send_account_approve_mail(approve_code, email, registration_id, testing_mode=False):
    """
    send_mail function returned:{
                                "id": "<20180123123620.1.8EAB0462E44DEEB5@mg.zops.io>",
                                "message": "Queued. Thank you."
                            }
    response_body['id'][1:-1] : 20180123123620.1.8EAB0462E44DEEB5@mg.zops.io

    :param approve_code:
    :param email:
    :param registration_id:
    :param testing_mode:
    :return:  mailgun mail id
    """
    url_data = urlencode({"registrationId": registration_id, "approveCode": approve_code, "email": email})
    mail_text = APPROVE_CODE_MAIL_TEXT.format(url=ZOPSM_APPROVE_URL, url_params=url_data)
    data = {
        "from": ADDRESS_FROM,
        "to": email,
        "subject": APPROVE_CODE_MAIL_SUBJECT,
        "text": mail_text,
        "h:X-Approve-Code": approve_code,
    }
    mail_id = send_mailgun(data, testing_mode)
    return {
        "id": mail_id,
        "text": mail_text,
        "subject": APPROVE_CODE_MAIL_SUBJECT
    }


def send_mailgun(data, testing_mode=False):
    """
    data format: {
              "from": ADDRESS_FROM,
              "to": "example@example.com,
              "subject": "Mail Subject,
              "text": "Mail Text",
                }
    if you want to send additional header , add data "h:X-Example-Header": "example data"
    :param data:
    :param testing_mode:
    :return:
    """
    if testing_mode:
        data['o:testmode'] = "true"

    data = urlencode(data)

    data = data.encode('ascii')

    auth_handler = request.HTTPBasicAuthHandler()
    auth_handler.add_password(realm='MG API', user="api", passwd=MAIL_GUN_API_KEY, uri=MAIL_GUN_URL)
    opener = request.build_opener(auth_handler)

    request.install_opener(opener)
    try:
        response = request.urlopen(MAIL_GUN_URL, data)
    except URLError as e:
        saas_logger.error("Send MailGun Raise Error: {}".format(e))
        raise HTTPFailedDependency(
            description="An error occurred while interacting with an external service, please try again later.")
    response_body = response.read()
    response_body = json.loads(response_body)
    mail_id = response_body['id'][1:-1]
    return mail_id


def delete_consumers_tokens(project_id, service_catalog_code):
    """
    We add    Key:refresh-token, Value:'P:{project_id}:S:{service}:RefTok:refresh-token'  in TokensKeys HashMap

    ('TokensKeys', 'refresh-token', 'P:{project_id}:S:{service}:RefTok:refresh-token')


    We add  {"account": "account_id","project": "project_id","service": "service_id","user": "user_id"} key value pair
    in 'P:{project_id}:S:{service}:RefTok:refresh-token' HashMap

    ('P:{project_id}:S:{service}:RefTok:refresh-token', {"account": "account_id",
                                                         "project": "project_id",
                                                         "service": "service_id",
                                                         "user": "user_id"
                                                         })

    If we want to remove user refresh and access token and user info in redis we delete all these token in redis
    """
    token_list_key = CACHE_SERVICE_TOKEN_LIST.format(
        project_id=project_id,
        service=service_catalog_code,
    )
    tokens_set_byte = cache.smembers(token_list_key)
    tokens_list = [token.decode() for token in tokens_set_byte]

    if tokens_list:
        tokens_value_byte = cache.hmget(CACHE_TOKENS_KEYS, tokens_list)
        tokens_value_list = [token_value.decode() for token_value in tokens_value_byte]

        cache.hdel(CACHE_TOKENS_KEYS, *tokens_list)
        cache.delete(*tokens_value_list)
        cache.delete(token_list_key)


def remove_user_tokens(user_id):
    """
    remove all user auth token in cache
    :param user_id:
    :return:
    """
    token_key = CACHE_SAAS_AUTH_TOKEN.format(user_id=user_id)
    cache.delete(token_key)


def add_user_token(user_id, token):
    token_key = CACHE_SAAS_AUTH_TOKEN.format(user_id=user_id)
    cache.sadd(token_key, token)


def remove_user_token(user_id, token):
    token_key = CACHE_SAAS_AUTH_TOKEN.format(user_id=user_id)
    cache.srem(token_key, token)


def is_user_token_exist(user_id, token):
    """
    token exist in user auth tokens
    :param user_id:
    :param token: user token
    :return: if user token exist return true, else false
    """
    token_key = CACHE_SAAS_AUTH_TOKEN.format(user_id=user_id)
    return cache.sismember(token_key, token)


def add_reset_password_token(token):
    return cache.sadd(CACHE_SAAS_RESET_PASSWORD_KEY, token)


def remove_reset_password_token(token):
    return cache.srem(CACHE_SAAS_RESET_PASSWORD_KEY, token)


def add_consumer_token(account_id, project_id, service_catalog_code, consumer_id, token):
    token_key = CACHE_REFRESH_TOKEN.format(
        project_id=project_id,
        service=service_catalog_code,
        token=token
    )

    cache.hmset(token_key, {
        "account": account_id,
        "project": project_id,
        "service": service_catalog_code,
        "user": consumer_id
    }
                )

    cache.expire(token_key, CACHE_REFRESH_TOKEN_EXPIRE_IN)
    cache.hset(CACHE_TOKENS_KEYS, token, token_key)


def remove_consumer_token(project_id, service_catalog_code, token):
    token_key = CACHE_REFRESH_TOKEN.format(
        project_id=project_id,
        service=service_catalog_code,
        token=token
    )

    t = cache.hget(CACHE_TOKENS_KEYS, token)

    if token_key != t.decode():
        raise HTTPBadRequest(description="Token does not found!.")

    cache.hdel(CACHE_TOKENS_KEYS, token)
    cache.delete(token_key)


def set_project_services_admin_token(project_id, token):
    token_key = PROJECT_SERVICES_ADMIN_TOKEN.format(project_id=project_id)
    cache.set(token_key, token)


def get_project_services_admin_token(project_id):
    token_key = PROJECT_SERVICES_ADMIN_TOKEN.format(project_id=project_id)
    return cache.get(token_key)


def add_project_services_admin_token(token, payload):
    cache.hmset(token, payload)
    cache.sadd(ADMIN_TOKENS, token)


def del_project_services_admin_token(admin_token):
    """Delete project services admin token in ADMIN_TOKENS key"""
    cache.delete(admin_token)
    cache.srem(ADMIN_TOKENS, admin_token)


