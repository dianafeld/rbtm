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

STEPS:

```
ssh mardanov@109.234.34.140 "cd rbtm/experiment && docker-compose stop"
cd ~/rbtm/drivers/tango_ds && source tango_env/bin/activate && ./run.sh > tango.log 2>&1

cd ~/rbtm/experiment && docker-compose build && docker-compose up -d > experiment.log 2>&1
ssh -T -N -g -R 5001:10.0.3.104:5001 mardanov@109.234.34.140 
```

NEW:

```
# expssh && 
#restart experiment docker container
docker restart experiment_server_1
docker restart drivers_server_1
cd ~/rbtm/drivers/tango_ds && ./run.sh
./stop.sh
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