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