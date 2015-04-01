# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('full_name', models.CharField(max_length=100, verbose_name=b'\xd0\xa4\xd0\x98\xd0\x9e')),
                ('role', models.CharField(default=b'GST', max_length=15, verbose_name=b'\xd0\xa0\xd0\xbe\xd0\xbb\xd1\x8c \xd0\xbd\xd0\xb0 \xd1\x81\xd0\xb0\xd0\xb9\xd1\x82\xd0\xb5', choices=[(b'ADM', b'\xd0\x90\xd0\xb4\xd0\xbc\xd0\xb8\xd0\xbd'), (b'EXP', b'\xd0\xad\xd0\xba\xd1\x81\xd0\xbf\xd0\xb5\xd1\x80\xd0\xb8\xd0\xbc\xd0\xb5\xd0\xbd\xd1\x82\xd0\xb0\xd1\x82\xd0\xbe\xd1\x80'), (b'RES', b'\xd0\x98\xd1\x81\xd1\x81\xd0\xbb\xd0\xb5\xd0\xb4\xd0\xbe\xd0\xb2\xd0\xb0\xd1\x82\xd0\xb5\xd0\xbb\xd1\x8c'), (b'GST', b'\xd0\x93\xd0\xbe\xd1\x81\xd1\x82\xd1\x8c')])),
                ('gender', models.CharField(default=b'N', max_length=6, verbose_name=b'\xd0\x9f\xd0\xbe\xd0\xbb', choices=[(b'F', b'\xd0\x96\xd0\xb5\xd0\xbd\xd1\x81\xd0\xba\xd0\xb8\xd0\xb9'), (b'M', b'\xd0\x9c\xd1\x83\xd0\xb6\xd1\x81\xd0\xba\xd0\xbe\xd0\xb9'), (b'N', b'\xd0\x9d\xd0\xb5 \xd1\x83\xd0\xba\xd0\xb0\xd0\xb7\xd0\xb0\xd0\xbd')])),
                ('phone_number', models.CharField(max_length=20, verbose_name=b'\xd0\xa2\xd0\xb5\xd0\xbb\xd0\xb5\xd1\x84\xd0\xbe\xd0\xbd', blank=True)),
                ('address', models.CharField(max_length=100, verbose_name=b'\xd0\x90\xd0\xb4\xd1\x80\xd0\xb5\xd1\x81', blank=True)),
                ('work_place', models.CharField(max_length=100, verbose_name=b'\xd0\x9c\xd0\xb5\xd1\x81\xd1\x82\xd0\xbe \xd1\x83\xd1\x87\xd1\x91\xd0\xb1\xd1\x8b/\xd1\x80\xd0\xb0\xd0\xb1\xd0\xbe\xd1\x82\xd1\x8b', blank=True)),
                ('degree', models.CharField(max_length=50, verbose_name=b'\xd0\xa3\xd1\x87\xd0\xb5\xd0\xbd\xd0\xb0\xd1\x8f \xd1\x81\xd1\x82\xd0\xb5\xd0\xbf\xd0\xb5\xd0\xbd\xd1\x8c', blank=True)),
                ('title', models.CharField(max_length=50, verbose_name=b'\xd0\x97\xd0\xb2\xd0\xb0\xd0\xbd\xd0\xb8\xd0\xb5', blank=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
