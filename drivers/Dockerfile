FROM ubuntu:trusty

MAINTAINER itsnotme

RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y wget python python-pip python-dev python-numpy \
                       libzmq3 libomniorb4-1 mysql-server python-pytango \
                       tango-common tango-db tango-starter libtango8 libtango8-dev liblog4tango5 liblog4tango5-dev \
 && rm -rf /var/lib/apt/lists/*

COPY requirements_docker.txt /var/www/drivers/requirements_docker.txt
WORKDIR /var/www/drivers/

RUN pip install -r requirements_docker.txt

COPY . /var/www/drivers/

RUN echo "TANGO_HOST=rbtm-tango:10000"

# setup supervisord
# RUN mkdir -p /var/log/supervisor
# RUN cp experiment_supervisord.conf /etc/supervisor/conf.d/

EXPOSE 10000
# CMD ["supervisord", "-n"]

RUN wget http://www.ximea.com/support/attachments/271/XIMEA_Linux_SP.tgz && tar -zxvf XIMEA_Linux_SP.tgz && cd package && ./install

RUN python setup.py build_ext

CMD ["tango_ds/run.sh"]