import falcon
import json
import os
from zopsm.lib.rest.authentication import zops_authorization_required
from graceful.resources.generic import RetrieveUpdateDeleteAPI, PaginatedListCreateAPI, \
    ListCreateAPI
from mimeparse import parse_mime_type
from zopsm.lib.settings import VIRTUAL_HOST
from zopsm.lib.rest.rpc import RpcClient
from zopsm.lib.sd_rabbit import rabbit_user, rabbit_pw

rabbit_nodes = json.loads(os.getenv('RABBIT_NODES'))
rabbit_host = list(rabbit_nodes.items())[0][1]

rpc_client = RpcClient(
    connection_params={
        "host": f'{rabbit_host}',
        "port": 5672,
        "virtual_host": VIRTUAL_HOST,
    },
    rabbitmq_user=rabbit_user,
    rabbitmq_pass=rabbit_pw,
    exchange=os.getenv('RABBIT_EXCHANGE', 'inter_comm'))


class ZopsRPC:
    def __init__(self):
        self.rpc_client = rpc_client


class ZopsBaseResource:
    allow_in_public_doc = True
    def require_representation(self, req):
        """Require raw representation dictionary from falcon request object.

        This does not perform any field parsing or validation but only uses
        allowed content-encoding handler to decode content body.

        Note:
            Currently only JSON is allowed as content type.

        Args:
            req (falcon.Request): request object

        Returns:
            dict: raw dictionary of representation supplied in request body

        """
        try:
            type_, subtype, _ = parse_mime_type(req.content_type)
            content_type = '/'.join((type_, subtype))
        except:
            raise falcon.HTTPUnsupportedMediaType(
                description="Invalid Content-Type header: {}".format(
                    req.content_type
                )
            )

        if content_type == 'application/json':
            body = req.stream.read()
            try:
                res = json.loads(body.decode('utf-8'))
            except json.decoder.JSONDecodeError:
                raise falcon.HTTPBadRequest(
                    title="Bad Request",
                    description="Body is not a valid json."
                )
            return res
        else:
            raise falcon.HTTPUnsupportedMediaType(
                description="only JSON supported, got: {}".format(content_type)
            )

    def describe(self, req=None, resp=None, **kwargs):
        return super().describe(
            req, resp,
            title=self.__repr__(),
            **kwargs
        )

    def allowed_methods(self):
        """Return list of allowed HTTP methods on this resource.

        This is only for purpose of making resource description.

        Returns:
            list: list of allowed HTTP method names (uppercase)

        """
        alloweds = []

        map = {
            "GET": ["retrieve", "list"],
            "POST": ["create"],
            "PUT": ["update"],
            "PATCH": ["create_bulk"],
            "DELETE": ["delete"],
            "HEAD": ["on_head"],
            "OPTIONS": ["on_options"]}

        for method in map.keys():
            attr_list = [getattr(self, m, False) for m in map[method]]
            if any(attr_list):
                for attr in attr_list:
                    if attr and attr.__doc__ != "Not Implemented":
                        alloweds.append(method)
        return alloweds

    def __repr__(self):
        return "Zops Base Resource"

    def __str__(self):
        return self.__repr__()


@zops_authorization_required
class ZopsRetrieveUpdateDeleteApi(ZopsRPC, ZopsBaseResource, RetrieveUpdateDeleteAPI,
                                  with_context=True):
    """
    Customized Generic Retrieve/Update API with resource serialization.

    Generic resource that uses serializer for resource description,
    serialization and validation.

    Additionally, with the help of send_to_pika method, this class can send messages through pika
    and returns falcon.HTTP_ACCEPTED to the client. When message is consumed, client will get it
    from its ws connection.

    Allowed methods:

    * GET: retrieve resource representation (handled with ``.retrieve()``
      method handler)
    * PUT: update resource with representation provided in request body
      (handled with ``.update()`` method handler)
    * DELETE: delete resource (handled with ``.delete()`` method handler)

    """

    @staticmethod
    def check_resource_id(resource_id):
        if not (resource_id and resource_id.isalnum()):
            raise falcon.HTTPBadRequest(
                title="Bad Request. Client sent a request which includes invalid resource id",
                description="Resource id '{}' is not alphanumeric".format(resource_id))


@zops_authorization_required
class ZopsPaginatedListCreateApi(ZopsRPC, ZopsBaseResource, PaginatedListCreateAPI,
                                 with_context=True):
    """
    Customized Generic List/Create API with resource serialization.

    Generic resource that uses serializer for resource description, serialization and validation.

    Does not allow bulk insert.

    Allowed methods:

    * GET: list multiple resource instances representations (handled
      with ``.list()`` method handler)
    * POST: create new resource from representation provided in request body
      (handled with ``.create()`` method handler)
    """

    def _create(self, params, meta, **kwargs):
        return self.serializer.to_representation(
            self.create(params, meta, **kwargs)
        )

    def on_post(self, req, resp, **kwargs):
        """Respond on POST HTTP request assuming resource creation flow.

        This request handler assumes that POST requests are associated with
        resource creation. Thus default flow for such requests is:

        * Validate the requests body.
        * Run resource creation callback by calling its default self.create method, and inside of
        that method send a creation demand to pika with fields that are included in body of the req.
        * Set response status code to ``202 Accepted``.

        Args:
            req (falcon.Request): request object instance.
            resp (falcon.Response): response object instance to be modified
            handler (method): creation method handler to be called. Defaults
                to ``self.create``.
            **kwargs: additional keyword arguments retrieved from url template.
        """
        super().on_post(req, resp, **kwargs)
        # obj = self.handle(
        #     handler or self.create, req, resp, **kwargs
        # )
        # try:
        #     resp.location = self.get_object_location(obj)
        # except NotImplementedError:
        #     pass
        #
        # resp.status = falcon.HTTP_CREATED
        resp.status = falcon.HTTP_ACCEPTED


@zops_authorization_required
class ZopsContinuatedListCreateApi(ZopsRPC, ZopsBaseResource, ListCreateAPI, with_context=True):
    """
    Customized Generic List/Create API with resource serialization.

    Generic resource that uses serializer for resource description, serialization and validation.

    Does not allow bulk insert.

    Allowed methods:

    * GET: list multiple resource instances representations (handled
      with ``.list()`` method handler)
    * POST: create new resource from representation provided in request body
      (handled with ``.create()`` method handler)
    """

    def _list(self, params, meta, **kwargs):
        listed_result = self.list(params, meta, **kwargs)
        return {
            "result": [
                self.serializer.to_representation(obj)
                for obj in listed_result['result']
            ],
            "continuation": listed_result['continuation']
        }

    def _create(self, params, meta, **kwargs):
        return self.serializer.to_representation(
            self.create(params, meta, **kwargs)
        )

    def on_post(self, req, resp, **kwargs):
        """Respond on POST HTTP request assuming resource creation flow.

        This request handler assumes that POST requests are associated with
        resource creation. Thus default flow for such requests is:

        * Validate the requests body.
        * Run resource creation callback by calling its default self.create method, and inside of
        that method send a creation demand to pika with fields that are included in body of the req.
        * Set response status code to ``202 Accepted``.

        Args:
            req (falcon.Request): request object instance.
            resp (falcon.Response): response object instance to be modified
            handler (method): creation method handler to be called. Defaults
                to ``self.create``.
            **kwargs: additional keyword arguments retrieved from url template.
        """
        super().on_post(req, resp, **kwargs)
        # obj = self.handle(
        #     handler or self.create, req, resp, **kwargs
        # )
        # try:
        #     resp.location = self.get_object_location(obj)
        # except NotImplementedError:
        #     pass
        #
        # resp.status = falcon.HTTP_CREATED
        resp.status = falcon.HTTP_ACCEPTED
