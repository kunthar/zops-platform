# ZopsM Base Image
#
# todo: install python packages by compiling cpython if possible
# pip install --no-binary :all: falcon
#

FROM python:3-alpine

#ADD credis /credis
COPY pfile.patch /pfile.patch
RUN set -x \
    && apk --update --no-cache add make python3-dev \
    && apk --update --no-cache --virtual .build-dep add \
        build-base gcc make g++ zlib-dev git \
    && pip install --upgrade pip \
    && pip install cython \
    && pip install pika \
    && pip install --no-binary :all: gevent \
    && pip install git+https://github.com/cablehead/python-consul \
    && pip install pyrabbit2 \
    && pip install python-logging-rabbitmq \
    && pip install gunicorn \
    && pip install hvac[parser] \
    && pip install hiredis \
    && pip install credis
#    && cd /credis \
#    && python setup.py build_ext --inplace \
#    && cp -r /credis/credis/ /usr/local/lib/python3.6/site-packages \
#    && apk del .build-dep

RUN patch -p 1 /usr/local/lib/python3.6/site-packages/consul/base.py -i /pfile.patch
RUN mkdir -p /usr/local/lib/python3.6/site-packages/zopsm
