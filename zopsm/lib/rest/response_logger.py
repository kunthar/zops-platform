from zopsm.lib.log_handler import zlogger


class ResponseLoggerMiddleware(object):
    def process_response(self, req, resp, resource, req_succeeded):
        status_code = resp.status[:3]
        user = req.context.get('user')
        if user:
           user = user.get('user')
        if status_code[:1] == '5' or status_code in ['401', '403', '408', '429']:
            zlogger.critical("{consumer} - {request_method} - {status_code} - {body}".format(
                consumer=user,
                request_method=req.method,
                status_code=status_code,
                body=resp.body,
            ))
