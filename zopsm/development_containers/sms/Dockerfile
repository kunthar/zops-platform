# ZetaOps SMS

FROM zetaops/zopsm-base
RUN set -x \
    && pip install graceful==0.6.3 \
    && pip install pydevd==1.4.0

CMD ["gunicorn", "-c", "/usr/local/lib/python3.6/site-packages/zopsm/sms/config.py", "zopsm.sms.server:app", "--timeout", "6000"]