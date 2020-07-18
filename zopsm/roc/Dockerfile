FROM python:3-alpine

RUN set -x \
    && apk --update --no-cache add make \
    && apk --update --no-cache --virtual .build-dep add \
        build-base \
    && pip install --upgrade pip \
    && pip install cython \
    && pip install --no-binary :all: falcon \
    && pip install gunicorn \
    && pip install gevent \
    && pip install graceful \
    && apk del .build-dep

WORKDIR /usr/src/app


VOLUME "/usr/src/app"

CMD gunicorn -b 0.0.0.0:3002  zgateway.server