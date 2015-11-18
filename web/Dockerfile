FROM ubuntu:trusty

MAINTAINER itsnotme

RUN apt-get update \
    && apt-get install -y python python-pip python-dev apache2 libapache2-mod-wsgi libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /var/www/web/requirements.txt
WORKDIR /var/www/web/

RUN pip install -r requirements.txt

COPY . /var/www/web/

RUN sed -i "s/'HOST': 'localhost'/'HOST': 'database'/" robotom/robotom/settings.py


RUN mkdir -p robotom/media && mkdir -p robotom/logs && \
    chown -R www-data:www-data robotom/media && chown -R www-data:www-data robotom/static && \
	touch robotom/logs/experiment.log && touch robotom/logs/storage.log && touch robotom/logs/main.log && \
	chown -R www-data:www-data robotom/logs && \
	touch robotom/rest.log && chown www-data:www-data robotom/rest.log

# ENV APACHE_RUN_USER www-data
# ENV APACHE_RUN_GROUP www-data
# ENV APACHE_LOG_DIR /var/log/apache2

# setup apache
RUN cp /var/www/web/000-default.conf /etc/apache2/sites-available/


RUN robotom/manage.py collectstatic --noinput

EXPOSE 80
CMD ["apache2ctl", "-D", "FOREGROUND"]
