echo "Stop Unit" > /var/log/unit/docker-entrypoint.log
pkill -f unit
pkill --signal SIGKILL unit
echo "Start Unit as non-daemon" >> /var/log/unit/docker-entrypoint.log
unitd --no-daemon --control 0.0.0.0:8000
echo "End" >> /var/log/unit/docker-entrypoint.log


