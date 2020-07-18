FROM nginx:stable-alpine
COPY default.conf /etc/nginx/conf.d/default.conf
COPY docs.conf /etc/nginx/conf.d/docs.conf
RUN apk --no-cache add shadow && groupadd -g 1001 ng && usermod -u 1001 nginx && usermod -g 1001 nginx \
    && mkdir -p /usr/share/nginx/zopsio && mkdir -p /usr/share/nginx/docs \
    && chown -R nginx:nginx /usr/share/nginx/zopsio \
    && chown -R nginx:nginx /usr/share/nginx/docs \
    && echo -n 'gogogo:$apr1$rIOd9CHr$IPgkByD8vUK8vmiSqhQ/3.' >> /etc/nginx/.htpasswd \
    && chown nginx:nginx /etc/nginx/.htpasswd

VOLUME /usr/share/nginx/zopsio
VOLUME /usr/share/nginx/docs
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]


#FROM nginx:stable-alpine
#COPY default.conf /etc/nginx/conf.d/default.conf
#COPY logs.conf /etc/nginx/conf.d/logs.conf
#COPY 3s.conf /etc/nginx/conf.d/3s.conf
#COPY www.conf /etc/nginx/conf.d/www.conf
#COPY ulakbusapi.conf /etc/nginx/conf.d/ulakbusapi.conf
#COPY ulakbus-cs.conf /etc/nginx/conf.d/ulakbus-cs.conf
#COPY .htpasswd /etc/nginx/.htpasswd