curl -X PUT --data-binary @/docker-entrypoint.d/${FAAS_APP_NAME}.pem http://localhost:8000/certificates/${FAAS_APP_NAME}
# curl -X PUT --data-binary @${FAAS_APP_NAME}.pem --unix-socket /unit/control.unit.sock http://localhost/certificates/${FAAS_APP_NAME}





