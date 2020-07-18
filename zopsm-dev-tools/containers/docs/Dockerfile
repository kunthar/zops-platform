FROM python:3-alpine

RUN set -x \
    && pip install --upgrade pip \
    && pip install grip \
    && pip install requests

COPY rest_api_render.py /rest_api_render.py
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]