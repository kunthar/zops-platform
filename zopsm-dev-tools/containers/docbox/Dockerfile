FROM node:9.2-slim

COPY entrypoint.sh /entrypoint.sh
RUN  chmod +x /entrypoint.sh \
     && apt-get update \
     && apt-get -y install git \
     && git clone https://github.com/zetaops/docbox

WORKDIR /docbox
RUN /usr/local/bin/npm install
ENTRYPOINT ["/entrypoint.sh"]