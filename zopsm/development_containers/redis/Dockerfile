FROM redis:4.0.11
COPY entrypoint.sh /entrypoint.sh
RUN mkdir -p /usr/local/etc/redis/ && chown -R redis:redis /usr/local/etc/redis/ && chmod +x /entrypoint.sh
ENTRYPOINT [ "/entrypoint.sh" ]