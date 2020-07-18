import consul
import falcon
import secrets
import os
from falcon import HTTPMethodNotAllowed, HTTPBadRequest, HTTPUnauthorized
from zopsm.lib.rest.serializers import ZopsBaseSerializer
from zopsm.lib.rest.fields import ZopsStringField
from zopsm.lib.rest.fields import ZopsIntegerField
from zopsm.lib.rest.custom import ZopsBaseResource
from zopsm.lib.credis import ZRedis
from zopsm.lib.sd_consul import consul_client
from zopsm.lib.sd_consul import EnvironmentVariableNotFound
from zopsm.lib.settings import CACHE_ACCESS_TOKEN
from zopsm.lib.settings import CACHE_REFRESH_TOKEN
from zopsm.lib.settings import CACHE_TOKENS_KEYS
from zopsm.lib.settings import CACHE_ACCESS_TOKEN_EXPIRES_IN
from zopsm.lib.settings import CACHE_SERVICE_TOKEN_LIST
from zopsm.lib.settings import WORKING_ENVIRONMENT
from zopsm.lib.rest.resource import ResourceListResource
from zopsm.lib.rest.resource import Ping
from graceful.resources.generic import ListCreateAPI
from zopsm.lib.sd_redis import redis_db_pw

container_name = os.getenv('CONTAINER_NAME', 'auth')
container_port = os.getenv('CONTAINER_PORT', 8000)
host_ipv4 = os.getenv('DOCKER_HOST_IPV4')
if host_ipv4 is None:
    raise EnvironmentVariableNotFound('DOCKER_HOST_IPV4 should not be empty.')

master = os.getenv('REDIS_MASTER')

if WORKING_ENVIRONMENT in ["zopsm", "develop"]:
    # Consul service and check registration
    check = consul.Check.http(
        url=f'http://{host_ipv4}:{container_port}/v1/ping',
        timeout='1s',
        interval='10s',
        deregister='2m')
    consul_client.agent.service.register(
        name='auth',
        service_id=f'{container_name}',
        address=f'{host_ipv4}',
        port=int(container_port),
        check=check)

cache = ZRedis(host=master,
               password=redis_db_pw,
               db=os.getenv('REDIS_DB'))


def generate_user_token(lenght=64):
    """
    Generates a urlsafe ascii default 40 byte length user auth token

    Args:
        lenght(int): length of token

    Returns: (str)

    """
    return secrets.token_urlsafe(lenght)


def validate_is_not_null(value):
    """
    Validates if value is not null or raise BadRequest

    Args:
        value (str): value

    """
    if value in ["", None, "None"]:
        raise HTTPBadRequest(
            title="Bad Request",
            description="Field cannot be null or empty string."
        )


class UserTokenSerializer(ZopsBaseSerializer):
    refreshToken = ZopsStringField("Token which is taken from SaaS or this resource previously. It "
                                   "does not expire unless updated.",
                                   source='refresh_token', validators=[validate_is_not_null])
    accessToken = ZopsStringField(
        "Token which is taken from this resource by POST request. Its expire time specified with "
        "the expiresIn field.",
        read_only=True, source='access_token', validators=[validate_is_not_null])
    expiresIn = ZopsIntegerField("Access token's expires time", read_only=True, source='expires_in',
                                 validators=[validate_is_not_null])


class UserTokenCreate(ZopsBaseResource, ListCreateAPI):
    """
    Allows to obtain access token.

    By using the refresh token which is obtained from saas api, access token with a 3 hours time to
    live, can be obtained from this endpoint.

    ### Code Examples:
    #### POST:
    ##### Request:
    ```bash

    curl \\
         --request POST \\
         --header "Content-Type: application/json; charset=utf-8" \\
         --data-binary "{                                                                       \\
                \"refreshToken\": \"qS2ZF-F97H6e8SeHoTF16bqDtwj6jCsLsGVK2Tx3aE4ks48TFjHvKeEK0YnYGAF4XUvubwGghYN1rmu_egblgg\" \\
         }" \\
         https://api_baseurl/v1/auth/token

    ```


    ```python
    import requests
    import json

    header = {"Content-Type": "application/json; charset=utf-8",
              "Authorization": "Token a3449bd777754fd1ab284ebcc8c878c23cea6b2295bd41ddbe289f03801402e6"}

    payload = {
        "refreshToken": "qS2ZF-F97H6e8SeHoTF16bqDtwj6jCsLsGVK2Tx3aE4ks48TFjHvKeEK0YnYGAF4XUvubwGghYN1rmu_egblgg"
    }

    req = requests.post("https://api_baseurl/v1/auth/token",
                                headers=header, data=json.dumps(payload))

    ```
    ##### Response:
    202 Accepted.
    ```json
    {
        "meta": {
            "params": {
                "indent": 0
            }
        },
        "content": {
            "refreshToken": "9sZp5xGp0BWf26N5k5U4lATcJTwpCA8NEPvfYWWs7h8jGwdwk0RTZv9_8o25nRg7QR6sIezf18jIREO0h4n15w",
            "accessToken": "1N5tscT85JahzozGY-hm8QzR6Ex8pbH40ajnBJu4sNKkWJOQlKrFYVRxqDxDf3iiST2hHlNzzT0jznApMfBxkI9SgiEYozZOOfYgnpCAtk_STKy7CagKZPsheDI0EypYorZNo0IIFLSDJilHH5qCTEA-g44pUVX0OoekH5ap8CQ",
            "expiresIn": 10800
        }
    }
    ```

    """

    def __repr__(self):
        return "Service Token Creation"

    def __str__(self):
        return self.__repr__()

    serializer = UserTokenSerializer()

    def list(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())

    def create(self, params, meta, **kwargs):
        validated = kwargs.get('validated')
        refresh_token = validated.get('refresh_token')
        new_refresh_token = generate_user_token()
        new_access_token = generate_user_token(lenght=128)

        # redis keys for tokens
        refresh_token_key = cache.hmget(CACHE_TOKENS_KEYS, refresh_token)[0]

        user_info_byte = cache.hgetall(refresh_token_key)
        if not user_info_byte:
            raise HTTPUnauthorized(
                title="Unauthorized",
                description="Invalid token"
            )
        user_info = {}
        for k, v in user_info_byte.items():
            user_info[k.decode()] = v.decode()

        new_refresh_token_key = CACHE_REFRESH_TOKEN.format(
            project_id=user_info.get('project'),
            service=user_info.get('service'),
            token=new_refresh_token,
        )
        new_access_token_key = CACHE_ACCESS_TOKEN.format(
            project_id=user_info.get('project'),
            service=user_info.get('service'),
            token=new_access_token,
        )

        cache_service_tokens_key = CACHE_SERVICE_TOKEN_LIST.format(
            project_id=user_info.get('project'),
            service=user_info.get('service')
        )

        # old access token
        access_token = user_info.pop('access_token', None)
        access_token_key = cache.hmget(CACHE_TOKENS_KEYS, access_token)[0]

        # delete old access token from redis
        cache.delete(access_token_key)
        cache.hdel(CACHE_TOKENS_KEYS, access_token)

        # add the access and refresh token in service_tokens
        cache.sadd(cache_service_tokens_key, new_access_token)
        cache.sadd(cache_service_tokens_key, new_refresh_token)

        # set the new access token
        cache.hmset(new_access_token_key, user_info)
        cache.hset(CACHE_TOKENS_KEYS, new_access_token, new_access_token_key)

        # update user_info with access token which corresponds to new refresh token
        user_info['access_token'] = new_access_token

        # set the new refresh token with updated user_info
        cache.hmset(new_refresh_token_key, user_info)
        cache.hset(CACHE_TOKENS_KEYS, new_refresh_token, new_refresh_token_key)

        # remove the old refresh token from redis
        cache.delete(refresh_token_key)
        cache.hdel(CACHE_TOKENS_KEYS, refresh_token)

        # set expire time for the access token
        cache.expire(new_access_token_key, CACHE_ACCESS_TOKEN_EXPIRES_IN)
        return {
            "refresh_token": new_refresh_token,
            "access_token": new_access_token,
            "expires_in": CACHE_ACCESS_TOKEN_EXPIRES_IN
        }

    def create_bulk(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())


# todo if we want to know client id and client secret we can match them with tokens, and get
# from header via Basic Auth

app = application = falcon.API()
endpoints = {
    "/v1/auth/token": UserTokenCreate()
}

for uri, endpoint in endpoints.items():
    app.add_route(uri, endpoint)

app.add_route("/", ResourceListResource(endpoints))
app.add_route("/v1/ping", Ping())
