echo "test" > /unit/test1
unitd --control 0.0.0.0:8000 --pid /unit/unit.pid --state /unit/ --tmp /unit/ --log /unit/unit.log
echo "test" > /unit/test2
export FAAS_APP_NAME=logstream-xc
echo "test" > /unit/test3
curl -X PUT --data-binary @/docker-entrypoint.d/${FAAS_APP_NAME}.pem http://localhost:8000/certificates/${FAAS_APP_NAME}
echo "test" > /unit/test4
curl -X PUT --data-binary @/docker-entrypoint.d/${FAAS_APP_NAME}.json http://localhost:8000/config/
echo "test" > /unit/test5
pkill -f unit
echo "test" > /unit/test6
rm -rf /var/lib/unit/certs
echo "test" > /unit/test7
rm -f /var/lib/unit/*
echo "test" > /unit/test8
unitd --no-daemon --control 0.0.0.0:8000 --pid /unit/unit.pid --state /unit/ --tmp /unit/ --log /unit/unit.log
echo "test" > /unit/test9





