# ZetaOps Messaging Transfer Agent

FROM  zetaops/zopsm-base
RUN set -x \
    && pip install --upgrade pip \
    && pip install pyparsing \
    && pip install riak \
    && pip install pushjack \
    && pip install hvac[parser]

#ADD zopsm /usr/local/lib/python3.6/site-packages/zopsm
CMD ["python", "-m", "zopsm.workers.server"]