# ZetaOps GateWay

FROM zetaops/zopsm-base
RUN set -x \
    && pip install tornado==4.5.3 \
    && pip install pydevd==1.4.0

ARG CACHEBUST=1
CMD ["gunicorn", "-c", "/usr/local/lib/python3.6/site-packages/zopsm/mda/config.py", "zopsm.mda.ws_handler:application", "--timeout", "6000"]
