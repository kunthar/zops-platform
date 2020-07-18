# ZetaOps SAAS

FROM zetaops/zopsm-base
RUN apk update \
  && apk --update --no-cache --virtual .build-dep add gcc python3-dev musl-dev postgresql-dev \
  && apk add postgresql-libs \
  && pip install psycopg2==2.7.3.1 \
  && apk del .build-dep

RUN set -x \
    && pip install falcon==1.3.0 \
    && pip install gevent==1.3.4 \
    && pip install graceful==0.5.0 \
    && pip install gunicorn==19.7.1 \
    && pip install PyJWT==1.5.3 \
    && pip install alembic==0.9.5 \
    && pip install SQLAlchemy==1.1.14 \
    && pip install ply==3.4 \
    && pip install pyhcl==0.2.3 \
    && pip install hvac[parser]==0.6.0 \
    && pip install pydevd==1.4.0

ARG CACHEBUST=1
CMD ["python3.6", "/usr/local/lib/python3.6/site-packages/zopsm/saas/wsgi.py"]
