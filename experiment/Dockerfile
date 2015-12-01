FROM ubuntu:trusty

MAINTAINER itsnotme

RUN apt-get update \
 && apt-get install -y python python-pip nginx supervisor pkg-config \
                       libfreetype6-dev python-numpy python-matplotlib python-scipy python-pytango \
 && rm -rf /var/lib/apt/lists/*

COPY requirements_docker.txt /var/www/experiment/requirements_docker.txt
WORKDIR /var/www/experiment/

RUN pip install -r requirements_docker.txt

COPY . /var/www/experiment/

RUN echo "STORAGE_FRAMES_URI = 'http://109.234.34.140:5016/storage/frames/post'\nSTORAGE_EXP_START_URI = 'http://109.234.34.140:5016/storage/experiments/create'\nSTORAGE_EXP_FINISH_URI = 'http://109.234.34.140:5016/storage/experiments/finish'" >> conf.py
RUN echo "WEBPAGE_URI = 'http://109.234.34.140:5021/take_image'" >> conf.py
RUN echo "TOMO_ADDR = '188.166.73.250:10000'" >> conf.py

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