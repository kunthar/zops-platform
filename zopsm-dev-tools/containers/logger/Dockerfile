FROM zetaops/zopsm-base

RUN set -x \
    && pip install --upgrade pip \
    && pip install riak \
    && awk '/self.queue.put/{print;print "\            import time\n\            time.sleep(0.01)";next}1' /usr/local/lib/python3.6/site-packages/python_logging_rabbitmq/handlers_oneway.py > handlers_oneway.py \
    && cat handlers_oneway.py > /usr/local/lib/python3.6/site-packages/python_logging_rabbitmq/handlers_oneway.py

#ADD zopsm /usr/local/lib/python3.6/site-packages/zopsm
ENTRYPOINT ["/usr/local/bin/python", "-m", "zopsm.log.run"]


