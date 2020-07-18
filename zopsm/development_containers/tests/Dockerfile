FROM zetaops/zopsm-base

ENV PYCURL_SSL_LIBRARY=openssl

RUN set -x \
  && apk --update --no-cache add openssl curl \
  && apk --update --no-cache --virtual .build-dep add gcc python3-dev musl-dev curl-dev \
  && pip install pyresttest \
  && apk del .build-dep

#ADD zopsm /usr/local/lib/python3.6/site-packages/zopsm
#COPY entrypoint.sh /entrypoint.sh
#RUN chmod +x /entrypoint.sh
#ENTRYPOINT ["/entrypoint.sh"]

