FROM ubuntu:trusty

MAINTAINER itsnotme

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN DEBIAN_FRONTEND=noninteractive  apt-get update \
 && apt-get install -y python python-pip nginx supervisor pkg-config \
                       libfreetype6-dev python-numpy python-matplotlib python-scipy python-pytango \
 && rm -rf /var/lib/apt/lists/*

COPY requirements_docker.txt /var/www/experiment/requirements_docker.txt
WORKDIR /var/www/experiment/

RUN pip install -r requirements_docker.txt

COPY . /var/www/experiment/

# setup nginx
RUN mkdir -p logs && echo "daemon off;" >> /etc/nginx/nginx.conf \
    && rm /etc/nginx/sites-enabled/default \
    && cp /var/www/experiment/experiment_nginx.conf /etc/nginx/sites-available/ \
    && ln -s /etc/nginx/sites-available/experiment_nginx.conf /etc/nginx/sites-enabled/

# setup supervisord
# RUN mkdir -p /var/log/supervisor
RUN cp experiment_supervisord.conf /etc/supervisor/conf.d/

EXPOSE 5001
CMD ["supervisord", "-n"]
