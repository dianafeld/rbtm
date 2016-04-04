# based on https://hub.docker.com/r/mliszcz/tango-cs/~/dockerfile/

FROM mliszcz/tango-cs

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

#RUN printf "\
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

RUN apt-get update && apt-get install -y wget python python-pip python-dev python-numpy python-pytango supervisor && \
    rm -rf /var/lib/apt/lists/*

# ROBO-TOM

COPY requirements_docker.txt /var/www/drivers/requirements_docker.txt
WORKDIR /var/www/drivers/

RUN pip install -r requirements_docker.txt

# detector
RUN wget http://www.ximea.com/support/attachments/271/XIMEA_Linux_SP.tgz && tar -zxvf XIMEA_Linux_SP.tgz && cd package
RUN ln -s /var/www/drivers/package/include /usr/include/m3api
# RUN echo "LD_LIBRARY_PATH=package/libs/libusb/X64/:package/libs/libraw1394/X64" >> ~/.bashrc

# motor 
RUN wget http://files.ximc.ru/libximc/ximc-2.8.7.tar.gz && tar -zxvf ximc-2.8.7.tar.gz && \
    cd ximc-2.8.7/ximc/deb && dpkg -i libximc7_2.8.7-1_amd64.deb libximc7-dev_2.8.7-1_amd64.deb && apt-get install -f

COPY . /var/www/drivers/

RUN cp drivers_supervisord.conf /etc/supervisor/conf.d/

#RUN service tango-db start && \
#    service tango-starter start && \
#    service tango-accesscontrol start
#    # /usr/lib/tango/TangoTest test

# RUN echo "TANGO_HOST=rbtm-tango:10000" >> ~/.bashrc


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