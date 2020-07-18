# ZopsM Base Image
#
# todo: install python packages by compiling cpython if possible
# pip install --no-binary :all: falcon
#

FROM python:3.6-alpine


RUN set -x \
    && apk --update --no-cache add make python3-dev \
    && apk --update --no-cache --virtual .build-dep add \
        build-base \
    && pip install cython==0.28.3 \
	&& pip install --no-binary :all: gevent==1.3.4 \
    && pip install pika==0.10.0 \
    && pip install python-consul==1.0.1 \
    && pip install pyrabbit2==1.0.5 \
    && pip install python-logging-rabbitmq==1.0.9 \
    && pip install gunicorn==19.7.1 \
    && pip install hiredis==0.2.0 \
    && pip install credis==1.0.8 \
    && pip install hvac[paser]==0.6.0 \
    && apk del .build-dep

RUN mkdir -p /usr/local/lib/python3.6/site-packages/zopsm
