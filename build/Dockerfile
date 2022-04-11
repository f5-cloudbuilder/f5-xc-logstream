# syntax=docker/dockerfile:1.3

############################################# Base image for Python #############################################
FROM nginx/unit:1.26.1-python3.10

# port used by the listener in config.json
EXPOSE 8080
EXPOSE 8443

RUN apt-get update \
	&& apt-get install --no-install-recommends --no-install-suggests -y tcpdump git curl net-tools iproute2 \
    && mkdir -p /var/log/unit/ \
    && touch /var/log/unit/access.log \
    && chown -R unit:0 /var/log/unit/ \
    && mkdir /etc/faas-apps/ \
    && chown -R unit:unit /etc/faas-apps/ \
    && mkdir -p /var/lib/unit/certs/ \
    && chmod 0774 /var/lib/unit/certs/ \
    && python3 -m venv /etc/faas-apps/venv

############################################# Create App's virtual environment #############################################
ARG FAAS_APP_NAME=logstream-xc
ARG GITHUB_USER=nergalex
ARG GITHUB_REPO=f5-xc-logstream
ARG GITHUB_BRANCH=master

RUN mkdir -p /etc/faas-apps/${FAAS_APP_NAME}/  \
ADD https://api.github.com/repos/${GITHUB_USER}/${GITHUB_REPO}/git/refs/heads/${GITHUB_BRANCH} version.json
RUN git clone -b ${GITHUB_BRANCH} https://github.com/${GITHUB_USER}/${GITHUB_REPO}.git /etc/faas-apps/${FAAS_APP_NAME} \
    && /etc/faas-apps/venv/bin/pip install -r /etc/faas-apps/${FAAS_APP_NAME}/requirements.txt

############################################# Clear Unit #############################################

RUN pkill -f unit
RUN cd /var/lib/unit && rm -rf *

############################################# Prepare Unit #############################################

COPY ./*.pem  /docker-entrypoint.d/
COPY ./*.json /docker-entrypoint.d/
COPY ./*.sh   /docker-entrypoint.d/
RUN chown unit:unit /docker-entrypoint.d/*.pem \
    && chown unit:unit /docker-entrypoint.d/*.json \
    && chown unit:unit /docker-entrypoint.d/*.sh \
    && chmod 444 /docker-entrypoint.d/*.pem \
    && chmod 444 /docker-entrypoint.d/*.json \
    && chmod 555 /docker-entrypoint.d/*.sh
RUN chown -R unit:unit /var/lib/unit/ \
    && chmod u+w /var/lib/unit/ \
    && chmod u+w /var/lib/unit/*

############################################# Launch Unit when container starts #############################################

CMD ["unitd", \
    "--no-daemon", \
    "--control", "0.0.0.0:8000", \
    "--pid", "/unit/unit.pid", \
    "--state", "/unit/",  \
    "--tmp", "/unit/",  \
    "--log", "/unit/unit.log"]

