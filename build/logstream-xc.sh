export FAAS_APP_NAME=logstream-xc
curl -X PUT --unix-socket /unit/control.unit.sock --data-binary @/docker-entrypoint.d/${FAAS_APP_NAME}.pem http://localhost/certificates/${FAAS_APP_NAME}
curl -X PUT --unix-socket /unit/control.unit.sock --data-binary @/docker-entrypoint.d/${FAAS_APP_NAME}.json http://localhost/config/





