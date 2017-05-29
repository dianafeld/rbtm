# based on https://hub.docker.com/r/mliszcz/tango-cs/~/dockerfile/

FROM buzmakov/tango-cs:stable

MAINTAINER itsnotme

# general

#ENV DEBIAN_FRONTEND=noninteractive \
#    DB_ROOT_PASSWORD=root \
#    TANGO_ADMIN_PASSWORD=root \
#    TANGO_APP_PASSWORD=root

# http://askubuntu.com/questions/365911/why-the-services-do-not-start-at-installation
#RUN printf '#!/bin/sh\nexit 0\n' > /usr/sbin/policy-rc.d

#RUN apt-get update && \
#    apt-get install -y debconf-utils


#  mysql-server mysql-server/root_password password ${DB_ROOT_PASSWORD}\n \
#  mysql-server mysql-server/root_password_again password ${DB_ROOT_PASSWORD}\n \
#  tango-common tango-common/tango-host string 127.0.0.1:10000\n \
#  tango-db tango-db/dbconfig-install boolean true\n \
#  tango-db tango-db/mysql/admin-pass password ${TANGO_ADMIN_PASSWORD}\n \
#  tango-db tango-db/mysql/app-pass password ${TANGO_APP_PASSWORD}" \
#    | debconf-set-selections

#RUN apt-get install -y mysql-server

#RUN service mysql start && \
#    apt-get install -y tango-db tango-accesscontrol tango-test
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y wget python python-pip python-dev python-numpy python-pytango supervisor libtiff-dev && \
    rm -rf /var/lib/apt/lists/*

# ROBO-TOM

COPY requirements_docker.txt /var/www/drivers/requirements_docker.txt
WORKDIR /var/www/drivers/

RUN pip install -r requirements_docker.txt

# motor 
RUN wget http://files.ximc.ru/libximc/libximc-2.8.7-all.tar.gz && tar -zxvf libximc-2.8.7-all.tar.gz && \
    cd ximc-2.8.7/ximc/deb && dpkg -i libximc7_2.8.7-1_amd64.deb libximc7-dev_2.8.7-1_amd64.deb && apt-get install -f

ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# detector
RUN wget http://www.ximea.com/downloads/recent/XIMEA_Linux_SP.tgz && tar -zxvf XIMEA_Linux_SP.tgz && cd package
RUN ln -s /var/www/drivers/package/include /usr/include/m3api
RUN ln -s /var/www/drivers/package/api/X64/libm3api.so* /usr/lib/ &&\
 ln -s /var/www/drivers/package/api/X64/libm3api.so.2 /usr/lib/libm3api.so &&\
 ldconfig

# RUN echo "LD_LIBRARY_PATH=package/libs/libusb/X64/:package/libs/libraw1394/X64" >> ~/.bashrc

#RUN service tango-db start && \
#    service tango-starter start && \
#    service tango-accesscontrol start
#    # /usr/lib/tango/TangoTest test

# RUN echo "TANGO_HOST=rbtm-tango:10000" >> ~/.bashrc

COPY . /var/www/drivers/
RUN cp drivers_supervisord.conf /etc/supervisor/conf.d/

RUN python setup.py build_ext

WORKDIR /var/www/drivers/tango_ds


EXPOSE 10000


CMD service mysql start && \
    service tango-db start && \
    service tango-starter start && \
    service tango-accesscontrol start && \
    ./add_to_db.py && \
    supervisord -n
 # 
