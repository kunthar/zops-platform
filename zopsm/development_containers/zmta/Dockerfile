# ZetaOps Messaging Transfer Agent

FROM  zetaops/zopsm-base
RUN set -x \
    && pip install pyparsing==2.2.0 \
    && pip install ply==3.4 \
    && pip install riak==2.7.0 \
    && pip install pushjack==1.4.1 \
    && pip install hvac[parser]==0.6.0 \
    && pip install pydevd==1.4.0


ARG CACHEBUST=1
CMD ["python3.6", "-m", "zopsm.workers.server"]
