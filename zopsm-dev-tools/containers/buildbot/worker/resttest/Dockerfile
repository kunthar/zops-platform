# buildbot/buildbot-worker

# please follow docker best practices
# https://docs.docker.com/engine/userguide/eng-image/dockerfile_best-practices/

# Provides a base Ubuntu (16.04) image with latest buildbot worker installed
# the worker image is not optimized for size, but rather uses ubuntu for wider package availability

FROM        ubuntu:16.04
MAINTAINER  Buildbot maintainers

RUN mkdir -p /buildbot
COPY ./worker.tac /buildbot/worker.tac

# Last build date - this can be updated whenever there are security updates so
# that everything is rebuilt
ENV         security_updates_as_of 2017-02-08

# This will make apt-get install without question
ARG         DEBIAN_FRONTEND=noninteractive

# Install security updates and required packages
RUN         apt-get update && \
            apt-get -y upgrade && \
            apt-get -y install -q \
                build-essential \
                git \
                subversion \
                python3 \
                python3-dev \
                python3-virtualenv \
                python3-pip \
                libffi-dev \
                libssl-dev \
                git \
                curl \
                httpie \
                python3-pycurl \
                jq \
                sudo && \
                pip3 install \
                   future \
                   pycurl \
                   pyyaml \
                   buildbot-worker && \
                git clone https://github.com/zetaops/pyresttest && \
                cd pyresttest/ && pip3 install . && \

            rm -rf /var/lib/apt/lists/* && \
# Test runs produce a great quantity of dead grandchild processes.  In a
# non-docker environment, these are automatically reaped by init (process 1),
# so we need to simulate that here.  See https://github.com/Yelp/dumb-init
            curl -Lo /usr/local/bin/dumb-init https://github.com/Yelp/dumb-init/releases/download/v1.1.3/dumb-init_1.1.3_amd64 && \
            chmod +x /usr/local/bin/dumb-init && \
# ubuntu pip version has issues so we should upgrade it: https://github.com/pypa/pip/pull/3287
            pip3 install virtualenv && \
# Install required python packages, and twisted
            pip3 --no-cache-dir install \
                'twisted[tls]' && \
    useradd -ms /bin/bash buildbot && chown -R buildbot /buildbot && \
    usermod -aG sudo buildbot && echo 'buildbot ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers && mkdir -p /home/buildbot/ssl && chown -R buildbot /home/buildbot/ssl
#
#COPY ssh-key.sh /buildbot/ssh-key.sh
#RUN chmod +x /buildbot/ssh-key.sh && chown buildbot /buildbot/ssh-key.sh
VOLUME ["/home/buildbot/ssl"]
VOLUME ["/var/log"]
RUN mkdir -p /home/buildbot/.ssh && mkdir -p /var/log/
COPY id_rsa /home/buildbot/.ssh/id_rsa
RUN chown -R buildbot:buildbot /home/buildbot/.ssh && chown -R buildbot:buildbot /var/log/ && chmod 0600 /home/buildbot/.ssh/id_rsa
USER buildbot
WORKDIR /buildbot

CMD ["/usr/local/bin/dumb-init", "twistd", "-ny", "worker.tac"]
