# ZetaOps GateWay

FROM zetaops/zopsm-base
RUN set -x \
    && pip install graceful==0.6.3 \
    && pip install pydevd==1.4.0

ARG CACHEBUST=1
CMD ["gunicorn", "-c", "/usr/local/lib/python3.6/site-packages/zopsm/auth/config.py", "zopsm.auth.server:app", "--timeout", "6000"]

