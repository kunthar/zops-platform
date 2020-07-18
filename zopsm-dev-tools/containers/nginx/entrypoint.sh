#!/usr/bin/env sh
set -x
chown -R nginx:nginx /usr/share/nginx/zopsio
chown -R nginx:nginx /usr/share/nginx/docs
nginx -g 'daemon off;'
set +x
