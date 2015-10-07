# based on https://hub.docker.com/r/mliszcz/tango-cs/~/dockerfile/

FROM ubuntu:trusty

MAINTAINER itsnotme

ENV DEBIAN_FRONTEND=noninteractive \
    DB_ROOT_PASSWORD=root \
    TANGO_ADMIN_PASSWORD=root \
    TANGO_APP_PASSWORD=root

# http://askubuntu.com/questions/365911/why-the-services-do-not-start-at-installation
RUN printf '#!/bin/sh\nexit 0\n' > /usr/sbin/policy-rc.d

RUN apt-get update && \
    apt-get install -y debconf-utils

RUN printf "\
  mysql-server mysql-server/root_password password ${DB_ROOT_PASSWORD}\n \
  mysql-server mysql-server/root_password_again password ${DB_ROOT_PASSWORD}\n \
  tango-common tango-common/tango-host string 127.0.0.1:10000\n \
  tango-db tango-db/dbconfig-install boolean true\n \
  tango-db tango-db/mysql/admin-pass password ${TANGO_ADMIN_PASSWORD}\n \
  tango-db tango-db/mysql/app-pass password ${TANGO_APP_PASSWORD}" \
    | debconf-set-selections

RUN apt-get install -y mysql-server

RUN service mysql start && \
    apt-get install -y tango-db tango-accesscontrol tango-test

RUN apt-get install -y wget python python-pip python-dev python-numpy python-pytango && \
    rm -rf /var/lib/apt/lists/*

COPY requirements_docker.txt /var/www/drivers/requirements_docker.txt
WORKDIR /var/www/drivers/

RUN pip install -r requirements_docker.txt

COPY . /var/www/drivers/

EXPOSE 10000

CMD service tango-db start && \
    service tango-starter start && \
    service tango-accesscontrol start && \
    /usr/lib/tango/TangoTest test

# RUN wget http://www.ximea.com/support/attachments/271/XIMEA_Linux_SP.tgz && tar -zxvf XIMEA_Linux_SP.tgz && cd package && ./install

# RUN python setup.py build_ext

# CMD ["tango_ds/run.sh"]

# RUN apt-get update \
# && DEBIAN_FRONTEND=noninteractive apt-get install -y wget python python-pip python-dev python-numpy \
#                       libzmq3 libomniorb4-1 mysql-server python-pytango \
#                       tango-common tango-db tango-starter libtango8 libtango8-dev liblog4tango5 liblog4tango5-dev \
# && rm -rf /var/lib/apt/lists/*


# COPY requirements_docker.txt /var/www/drivers/requirements_docker.txt
# WORKDIR /var/www/drivers/

# RUN pip install -r requirements_docker.txt

# COPY . /var/www/drivers/

# RUN echo "TANGO_HOST=rbtm-tango:10000"