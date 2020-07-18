# ZetaOps GateWay

FROM zetaops/zopsm-base
RUN set -x \
    && pip install --upgrade pip \
    && pip install graceful

#ADD zopsm /usr/local/lib/python3.6/site-packages/zopsm
CMD ["gunicorn", "-c", "/usr/local/lib/python3.6/site-packages/zopsm/auth/config.py", "zopsm.auth.server:app"]

