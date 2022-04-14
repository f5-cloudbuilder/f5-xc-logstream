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
    && python3 -m venv /etc/faas-apps/venv

############################################# Create App's virtual environment #############################################
ARG FAAS_APP_NAME
ARG GITHUB_BASE_REF
ARG GITHUB_REPOSITORY

RUN mkdir -p /etc/faas-apps/${FAAS_APP_NAME}/
ADD https://api.github.com/repos/${GITHUB_REPOSITORY}/git/refs/heads/${GITHUB_BASE_REF} version.json
RUN git clone -b ${GITHUB_BASE_REF} https://github.com/${GITHUB_REPOSITORY}.git /etc/faas-apps/${FAAS_APP_NAME} \
    && /etc/faas-apps/venv/bin/pip install -r /etc/faas-apps/${FAAS_APP_NAME}/requirements.txt


############################################# Prepare Unit #############################################

ARG BUILD_PATH

COPY ${BUILD_PATH}/*.pem  /docker-entrypoint.d/
RUN echo "" >> /docker-entrypoint.d/logstream-xc.pem \
  && echo $LOGSTREAM_XC_PEM_PRIVATE_KEYS | base64 -d >> /docker-entrypoint.d/logstream-xc.pem
COPY ${BUILD_PATH}/*.json /docker-entrypoint.d/
COPY ${BUILD_PATH}/*.sh   /docker-entrypoint.d/
RUN chown unit:unit /docker-entrypoint.d/*.pem \
    && chown unit:unit /docker-entrypoint.d/*.json \
    && chown unit:unit /docker-entrypoint.d/*.sh \
    && chmod 444 /docker-entrypoint.d/*.pem \
    && chmod 444 /docker-entrypoint.d/*.json \
    && chmod 555 /docker-entrypoint.d/*.sh


############################################# Launch Unit when container starts #############################################
CMD ["/docker-entrypoint.d/logstream-xc.sh"]



