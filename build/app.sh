curl -X PUT --data-binary @/docker-entrypoint.d/${FAAS_APP_NAME}.json http://localhost:8000/config/
# curl -X PUT --data-binary @${FAAS_APP_NAME}.json --unix-socket /unit/control.unit.sock http://localhost/config/





