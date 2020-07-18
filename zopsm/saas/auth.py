# -*- coding: utf-8 -*-

import functools
from falcon import HTTPMethodNotAllowed, HTTPUnauthorized
from zopsm.saas.models.user import ERoles
from zopsm.saas.utility import decode_jwt_token, is_user_token_exist

VIEWS = {}

method_map = {"retrieve": "GET",
              "list": "GET",
              "update": "PUT",
              "create": "POST",
              "delete": "DELETE"}


def require_roles(roles):
    def decorate(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        func_name = func.__repr__().split(' ')[1].split('.')
        methods = VIEWS.get(func_name[0], None)
        if methods is None:
            VIEWS[func_name[0]] = {}
        VIEWS[func_name[0]][method_map[func_name[1]]] = roles
        return wrapper

    return decorate


class AuthorizationMiddleware(object):
    """
    Middleware checks that:
        - Compare the allowed methods on resource and request method.
        - JWT token validation and existence
        - Check client's token role and allowed roles on resource.

    Middleware sends the JWT token the Resource.
    """

    def process_resource(self, req, resp, resource, params):
        resource_name = resource.resource_name()

        if VIEWS.get(resource_name) is None:
            #todo: log request no needs authorization resource_name
            return

        roles = VIEWS.get(resource_name).get(req.method)

        # Method not allowed or OPTIONS
        if roles is None:
            if req.method != "OPTIONS":
                raise HTTPMethodNotAllowed(description="Method not allowed for this resource",
                                           allowed_methods=[])
            return

        # Public resource.
        if ERoles.anonym in roles:
            return

        jwt_token = req.headers.get('AUTHORIZATION', None)
        if jwt_token is None:
            raise HTTPUnauthorized(description="Please, send a Authorization token.")

        payload = decode_jwt_token(jwt_token, "Authorization")

        if is_user_token_exist(payload['sub'], jwt_token):
            rol = ERoles(payload['rol'])
            if rol in roles:
                params['token'] = payload  # Send JWT token to the Resource.
                return
            raise HTTPUnauthorized(description="You can not access this resource.")
        raise HTTPUnauthorized(description="This token is no longer valid.")
