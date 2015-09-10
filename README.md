# rbtm
desc


109.234.34.140

http://109.234.38.83/


### Полезные команды
ssh -T -N -g -R 5001:10.0.3.104:5001 mardanov@109.234.34.140

docker-compose build && docker-compose up
docker exec -i -t storage_server_1 /bin/bash

mongorestore --drop storage_mongodump_clean/

# Delete all containers
docker rm $(docker ps -a -q)
# Delete all images
docker rmi $(docker images -q)
