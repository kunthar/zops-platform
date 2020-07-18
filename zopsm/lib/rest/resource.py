from graceful.resources.generic import PaginatedListAPI
from graceful.serializers import BaseSerializer
from graceful.fields import RawField
from graceful.resources.generic import Resource


class URLSerializer(BaseSerializer):
    url = RawField("url", read_only=True)


class ResourceListResource(PaginatedListAPI):
    serializer = URLSerializer()

    def list(self, params, meta, **kwargs):
        return [{"url": url} for url, cls_instance in self.endpoints.items() if cls_instance.allow_in_public_doc]


    def __repr__(self):
        return "ResourceListResource"

    def resource_name(self):
        return "ResourceListResource"

    def __init__(self, endpoints):
        self.endpoints = endpoints


class Ping(Resource):
    allow_in_public_doc = False

    def __repr__(self):
        return "Ping"

    def resource_name(self):
        return "Ping"

    def retrieve(self, params, meta, **kwargs):
        return "pong"

