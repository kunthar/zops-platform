FROM node:9.2-slim

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
                sudo \
                build-essential \
                git \
                subversion \
                python-dev \
                libffi-dev \
                libssl-dev \
                python-pip \
                curl \
                httpie \
                git \
                python-pycurl \
                jq && \
                pip install -U pip && \
                pip install -U setuptools && \
                pip install \
                   pyresttest \
                   future \
                   pycurl \
                   pyyaml \
                   buildbot-worker && \

            rm -rf /var/lib/apt/lists/* && \
# Test runs produce a great quantity of dead grandchild processes.  In a
# non-docker environment, these are automatically reaped by init (process 1),
# so we need to simulate that here.  See https://github.com/Yelp/dumb-init
            curl -Lo /usr/local/bin/dumb-init https://github.com/Yelp/dumb-init/releases/download/v1.1.3/dumb-init_1.1.3_amd64 && \
            chmod +x /usr/local/bin/dumb-init && \
# ubuntu pip version has issues so we should upgrade it: https://github.com/pypa/pip/pull/3287
            pip install virtualenv && \
# Install required python packages, and twisted
            pip install \
                'twisted[tls]' && \
    useradd -ms /bin/bash buildbot && chown -R buildbot /buildbot && \
    usermod -aG sudo buildbot && echo 'buildbot ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers && mkdir -p /home/buildbot/ssl && chown -R buildbot /home/buildbot/ssl

COPY ssh-key.sh /buildbot/ssh-key.sh
RUN chmod +x /buildbot/ssh-key.sh && chown buildbot /buildbot/ssh-key.sh
VOLUME ["/home/buildbot/ssl"]
RUN mkdir -p /home/buildbot/.ssh
COPY id_rsa /home/buildbot/.ssh/id_rsa
RUN chown -R buildbot:buildbot /home/buildbot/.ssh && chmod 0600 /home/buildbot/.ssh/id_rsa
USER buildbot
WORKDIR /buildbot

CMD ["/usr/local/bin/dumb-init", "twistd", "-ny", "worker.tac"]


