pkill -f unit
unitd --no-daemon --control 0.0.0.0:8000 --pid /unit/unit.pid --state /unit/ --tmp /unit/ --log /unit/unit.log
export FAAS_APP_NAME=logstream-xc
curl -X PUT --data-binary @/docker-entrypoint.d/${FAAS_APP_NAME}.pem http://localhost:8000/certificates/${FAAS_APP_NAME}
curl -X PUT --data-binary @/docker-entrypoint.d/${FAAS_APP_NAME}.json http://localhost:8000/config/



