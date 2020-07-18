# -*- coding: utf-8 -*-

from zopsm.saas.server import app
from wsgiref import simple_server

if __name__ == '__main__':
    httpd = simple_server.make_server('0.0.0.0', 8000, app)
    httpd.serve_forever()
