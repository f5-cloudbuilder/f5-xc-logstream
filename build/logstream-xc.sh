curl -X PUT --data-binary @/docker-entrypoint.d/${FAAS_APP_NAME}.pem --unix-socket /unit/control.unit.sock http://localhost/certificates/${FAAS_APP_NAME}
curl -X PUT --data-binary @/docker-entrypoint.d/${FAAS_APP_NAME}.json --unix-socket /unit/control.unit.sock http://localhost/config/






