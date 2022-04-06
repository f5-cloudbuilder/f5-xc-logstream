export FAAS_APP_NAME=logstream-xc
curl -X PUT --data-binary @${FAAS_APP_NAME}.json http://localhost:8080/config/
# curl -X PUT --data-binary @${FAAS_APP_NAME}.json --unix-socket /unit/control.unit.sock http://localhost/config/





