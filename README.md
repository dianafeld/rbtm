# ROBO-TOM
A service-oriented web application for carrying out computed tomography experiments with data processing (numpy, scipy) and visualization. Currently used in the laboratory in Institute of Crystallograhy. The system enables multiple users to take CT scans, store (mongoDB, HDF5) and browse collected imagery via a web-based UI (Django, Flask) operating on top of a TANGO-based network interface to CT hardware.

http://xtomo.ru

Documentation: http://rbtm.readthedocs.org/

# Usage howto
```
pg_dump -h localhost -p 15432 -U postgres robotom_users > robotom_users_dump_<date>
restore:
createdb -h localhost -p 15432 -U postgres -T template0 robotom_users
psql -h localhost -p 15432 -U postgres robotom_users < robotom_users_dump_<date>
```


NEW:

Если не работает streamView или двигатели выполнить команду:
```sh
docker stop drivers_server_1 experiment_server_1 
```

Если не работет томограф, то убедиться, что источник прогрет и выполнить:

```sh
~/rbtm/drivers/restart.sh
```

BUILD:

```
cd ~/rbtm/drivers/tango_ds
source tango_env/bin/activate
sudo rm /home/robotom/rbtm/drivers/logs/*.log
cd ../../drivers
docker-compose build
docker-compose up -d
```

Configure port forwarding

```
#crontab -e 
@reboot autossh -M 20100 -f -N -R 5080:localhost:5080 makov@109.234.38.83
@reboot autossh -M 20110 -f -N -R 5443:localhost:5443 makov@109.234.38.83
```

To configure iptables on the gate (add to the start of /etc/ufw/before/rules:

```
*nat
:PREROUTING ACCEPT [0:0]
-A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 5080
-A PREROUTING -p tcp --dport 443 -j REDIRECT --to-port 5443
COMMIT
```