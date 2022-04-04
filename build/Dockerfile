# syntax=docker/dockerfile:1.3

############################################# Base image for Python #############################################
FROM nginx/unit:1.26.1-python3.10

# port used by the listener in config.json
EXPOSE 8080

RUN apt-get update \
	&& apt-get install --no-install-recommends --no-install-suggests -y tcpdump git curl python-setuptools \
    && mkdir -p /var/log/unit/ \
    && touch /var/log/unit/access.log \
    && chown -R unit:0 /var/log/unit/ \
    && mkdir /etc/faas-apps/ \
    && chown -R unit:unit /etc/faas-apps/ \
    && pip3 install virtualenv setuptools \
    && python3 -m venv /etc/faas-apps/venv \
    && source /etc/faas-apps/venv/bin/activate \
    && deactivate

############################################# Create App's virtual environment #############################################
ARG FAAS_APP_NAME=logstream-xc
ARG FAAS_APP_REPO=https://github.com/nergalex/f5-xc-logstream.git

RUN mkdir -p /etc/faas-apps/${FAAS_APP_NAME}/  \
    && git clone ${FAAS_APP_REPO} /etc/faas-apps/${FAAS_APP_NAME} \
    && source /etc/faas-apps/venv/bin/activate \
    && pip install -r /etc/faas-apps/${FAAS_APP_NAME}/requirements.txt \
    && deactivate \
    && chown -R unit:unit /etc/faas-apps/${FAAS_APP_NAME}/ \
    && chmod 0775 /etc/faas-apps/${FAAS_APP_NAME}/declaration.json \
    && chmod 0775 /etc/faas-apps/${FAAS_APP_NAME}/logstream.log

############################################# Create a virtual environment #############################################

COPY ./*.pem  /docker-entrypoint.d/
COPY ./*.json /docker-entrypoint.d/
COPY ./*.sh   /docker-entrypoint.d/





