from falcon.errors import HTTPMethodNotAllowed
from graceful.fields import StringField
from graceful.parameters import StringParam
from graceful.resources.generic import ListCreateAPI, PaginatedListAPI
from zopsm.lib.rest.fields import ZopsJsonObjectField, ZopsDatetimeField
from zopsm.lib.rest.serializers import ZopsBaseSerializer
from zopsm.saas.validators import log_level_validator
from zopsm.saas.auth import require_roles
from zopsm.saas.models import ERoles, Log
from zopsm.saas.resources.saas_base import SaasBase


class LogNotifierSerializer(ZopsBaseSerializer):
    notifierData = ZopsJsonObjectField("Notifier data", write_only=True, source='notifier_data')


class LogTrackingSerializer(ZopsBaseSerializer):
    id = StringField("ID", read_only=True)
    description = StringField("Log Message", read_only=True)
    levelName = StringField("Log Level Name", read_only=True, source="level_name")
    functionName = StringField("Log Function Name", read_only=True, source="function_name")
    pathName = StringField("Log path name", read_only=True, source="path_name")
    lineNumber = StringField("Log line number", read_only=True, source="line_number")
    creationTime = ZopsDatetimeField("Log Creation Time", read_only=True, source="creation_time")


class LogNotifierResource(SaasBase, ListCreateAPI):

    allow_in_public_doc = False
    serializer = LogNotifierSerializer()

    def __repr__(self):
        return "Log Notifier"

    def resource_name(self):
        return "LogNotifierResource"

    def create(self, params, meta, **kwargs):
        """
        log message format = { "level_name": WARNING,
                               "function_name": find_redis_role,
                               "path_name": /usr/local/lib/python3.6/site-packages/zopsm/lib/sd_redis.py,
                               "line_number": 37,
                               "message": NOAUTH Authentication required.}
        """
        notifier_data = kwargs['validated']['notifier_data']
        for data in notifier_data:
            log_object = Log(level_name=data['level_name'],
                             function_name=data['function_name'],
                             description=data['message'],
                             line_number=data['line_number'],
                             path_name=data['path_name'])
            self.db.session.add(log_object)
        return {}

    def list(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())

    def create_bulk(self, params, meta, **kwargs):
        """Not Implemented"""
        raise HTTPMethodNotAllowed(self.allowed_methods())


class LogTrackingResource(SaasBase, PaginatedListAPI):
    """
    Log Tracking Resource
    #### GET
    Retrieve logs with level_name, function_name, page_size ang page params. Only manager user use these resource.
    page_size default value is 10.
    page default value is 0.
    #### Request:

    ```bash
        #bash
        curl \\
             --request GET                                                          \\
             --header "Content-Type: application/json"                              \\
             --header "AUTHORIZATION: 0sOEQfyptM0ZG7kJYkNxmswp_p5y9iX5t61KI1qH83w"  \\
             https://api_baseurl/api/v1/log-tracking?level_name=ERROR&page_size=5&page=1&function_name=find_redis_role
    ```

    ```python
        #pyhon
        import requests
        import json

        header = {
                    "Content-Type": "application/json",
                    "AUTHORIZATION": "0sOEQfyptM0ZG7kJYkNxmswp_p5y9iX5t61KI1qH83w"
                  }
        req = requests.get("https://api_baseurl/api/v1/log-tracking?level_name=ERROR&page_size=5&page=1&function_name=find_redis_role",
                                        header=header)
    ```

    #### Response:
    200 OK.
    ```json
        {
        "content": [
            {
                "amount": "7",
                "creationTime": "2018-02-06 15:55:51.628340",
                "description": "NOAUTH Authentication required.",
                "functionName": "find_redis_role",
                "id": "ba37d570c3364a0abf6681133552ed06",
                "levelName": "ERROR"
            }
        ],
        "meta": {
            "next": "page=2&page_size=5",
            "page": 1,
            "page_size": 5,
            "params": {
                "function_name": "find_redis_role",
                "indent": 0,
                "level_name": "ERROR",
                "page": 1,
                "page_size": 5
            },
            "prev": "page=0&page_size=5"
        }
        }
    ```
    """

    allow_in_public_doc = False
    serializer = LogTrackingSerializer()

    level_name = StringParam("Filter logs by log level. Log level type : WARNING, ERROR",
                             validators=[log_level_validator])
    function_name = StringParam("Filter logs by function_name")

    def __repr__(self):
        return "Log Tracking"

    def resource_name(self):
        return "LogTrackingResource"

    @require_roles(roles=[ERoles.manager])
    def list(self, params, meta, **kwargs):
        page_size = params["page_size"]
        page = params["page"]

        filter_params = {key: value for key, value in params.items() if key not in ['page_size', 'page', 'indent']}
        logs = self.db.paginated_filter(model=Log, order_field=Log.creation_time, page_size=page_size, page=page, **filter_params)

        if self.db.count(Log, **filter_params) > (page_size + 1) * page:
            meta['has_more'] = True
        return logs

