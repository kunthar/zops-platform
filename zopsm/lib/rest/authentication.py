from graceful.authentication import KeyValueUserStorage
from zopsm.lib.credis import ZRedis
from graceful.authorization import _before
from falcon import HTTPUnauthorized
from zopsm.lib.settings import CACHE_TOKENS_KEYS, ADMIN_TOKENS
import os

slave = os.getenv('REDIS_SLAVE')


class ZopsKeyValueUserStorage(KeyValueUserStorage):
    def __init__(self):
        super(ZopsKeyValueUserStorage, self).__init__(ZRedis(host=slave, db=os.getenv('REDIS_DB')))

    def get_user(self, identified_with, identifier, req, resp, resource, uri_kwargs):
        """Get user object for given identifier.

        Args:
            identified_with (object): authentication middleware used
                to identify the user.
            identifier: middleware specific user identifier (string or tuple
                in case of all built in authentication middleware classes).

        Returns:
            dict: user object stored in Redis if it exists, otherwise ``None``
        """

        token_key = self.kv_store.hmget(CACHE_TOKENS_KEYS, identifier)[0]

        stored_value = self.kv_store.hgetall(token_key)
        user = {}
        if stored_value:
            for k, v in stored_value.items():
                user[k.decode()] = v.decode()
        else:
            from zopsm.roc.server import roc_admin_endpoints
            admin_endpoints = {}
            admin_endpoints.update(roc_admin_endpoints)
            if req.uri_template in admin_endpoints.keys():
                if self.kv_store.sismember(ADMIN_TOKENS, identifier):
                    admin_info = self.kv_store.hgetall(identifier)
                    for k,v in admin_info.items():
                        user[k.decode()] = v.decode()

                    return user
            user = None

        return user


@_before
def zops_authorization_required(req, resp, resource, uri_kwargs):
    """Ensure that user is authenticated or request's method is OPTIONS
    otherwise return ``401 Unauthorized``.

    If request fails to authenticate this authorization hook will also
    include list of ``WWW-Athenticate`` challenges.

    Args:
        req (falcon.Request): the request object.
        resp (falcon.Response): the response object.
        resource (object): the resource object.
        uri_kwargs (dict): keyword arguments from the URI template.

    .. versionadded:: 0.4.0
    """

    if req.method == "OPTIONS":
        return

    if 'user' not in req.context:
        args = ["Unauthorized", "This resource requires authentication",
                req.context.get('challenges', [])]
        raise HTTPUnauthorized(*args)
