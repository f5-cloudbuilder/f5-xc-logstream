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
ARG FAAS_APP_REPO=https://github.com/nergalex/f5-xc-logstream.git

RUN mkdir -p /etc/faas-apps/${FAAS_APP_NAME}/  \
    && git clone ${FAAS_APP_REPO} /etc/faas-apps/${FAAS_APP_NAME} \
    && /etc/faas-apps/venv/bin/pip install -r /etc/faas-apps/${FAAS_APP_NAME}/requirements.txt \
    && chown -R unit:unit /etc/faas-apps/${FAAS_APP_NAME}/ \
    && chmod 0775 /etc/faas-apps/${FAAS_APP_NAME}/declaration.json \
    && chmod 0775 /etc/faas-apps/${FAAS_APP_NAME}/logstream.log

############################################# Configure Unit #############################################

COPY ./*.pem  /docker-entrypoint.d/
COPY ./*.json /docker-entrypoint.d/
COPY ./*.sh   /docker-entrypoint.d/
CMD ["unitd", \
    "--no-daemon", \
    "--control", "0.0.0.0:8000", \
    "--pid", "/unit/unit.pid", \
    "--state", "/unit/",  \
    "--tmp", "/unit/",  \
    "--log", "/unit/unit.log"]

