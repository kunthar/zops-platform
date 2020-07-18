# ZetaOps GateWay

FROM zetaops/zopsm-base
RUN set -x \
    && pip install pyparsing==2.2.0 \
    && pip install graceful==0.6.3 \
    && pip install pydevd==1.4.0

ARG CACHEBUST=1

CMD ["gunicorn", "-c", "/usr/local/lib/python3.6/site-packages/zopsm/push/config.py", "zopsm.push.server:app", "--timeout", "6000"]
