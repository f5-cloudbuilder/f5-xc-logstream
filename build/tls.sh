export FAAS_APP_NAME=logstream-xc
curl -X PUT --data-binary @${FAAS_APP_NAME}.pem http://localhost:8080/certificates/${FAAS_APP_NAME}
# curl -X PUT --data-binary @${FAAS_APP_NAME}.pem --unix-socket /unit/control.unit.sock http://localhost/certificates/${FAAS_APP_NAME}





