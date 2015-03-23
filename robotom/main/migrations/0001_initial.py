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
                ('middlename', models.CharField(max_length=50, verbose_name=b'Middlename', blank=True)),
                ('role', models.CharField(default=b'GST', max_length=15, verbose_name=b'User role', choices=[(b'ADM', b'Admin'), (b'EXP', b'Experimentator'), (b'RES', b'Researcher'), (b'GST', b'Guest')])),
                ('gender', models.CharField(default=b'N', max_length=6, verbose_name=b'Gender', choices=[(b'F', b'Female'), (b'M', b'Male'), (b'N', b'Not stated')])),
                ('phone_number', models.CharField(max_length=20, verbose_name=b'Phone', blank=True)),
                ('address', models.CharField(max_length=100, verbose_name=b'Address', blank=True)),
                ('work_place', models.CharField(max_length=100, verbose_name=b'Work/study place', blank=True)),
                ('degree', models.CharField(max_length=50, verbose_name=b'Degree', blank=True)),
                ('title', models.CharField(max_length=50, verbose_name=b'Academic title', blank=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
