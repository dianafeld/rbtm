# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20150323_1417'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='middlename',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='full_name',
            field=models.CharField(default='Name Surname', max_length=100, verbose_name=b'\xd0\xa4\xd0\x98\xd0\x9e'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='address',
            field=models.CharField(max_length=100, verbose_name=b'\xd0\x90\xd0\xb4\xd1\x80\xd0\xb5\xd1\x81', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='degree',
            field=models.CharField(max_length=50, verbose_name=b'\xd0\xa3\xd1\x87\xd0\xb5\xd0\xbd\xd0\xb0\xd1\x8f \xd1\x81\xd1\x82\xd0\xb5\xd0\xbf\xd0\xb5\xd0\xbd\xd1\x8c', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='gender',
            field=models.CharField(default=b'N', max_length=6, verbose_name=b'\xd0\x9f\xd0\xbe\xd0\xbb', choices=[(b'F', b'\xd0\x96\xd0\xb5\xd0\xbd\xd1\x81\xd0\xba\xd0\xb8\xd0\xb9'), (b'M', b'\xd0\x9c\xd1\x83\xd0\xb6\xd1\x81\xd0\xba\xd0\xbe\xd0\xb9'), (b'N', b'\xd0\x9d\xd0\xb5 \xd1\x83\xd0\xba\xd0\xb0\xd0\xb7\xd0\xb0\xd0\xbd')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='phone_number',
            field=models.CharField(max_length=20, verbose_name=b'\xd0\xa2\xd0\xb5\xd0\xbb\xd0\xb5\xd1\x84\xd0\xbe\xd0\xbd', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='title',
            field=models.CharField(max_length=50, verbose_name=b'\xd0\x97\xd0\xb2\xd0\xb0\xd0\xbd\xd0\xb8\xd0\xb5', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='work_place',
            field=models.CharField(max_length=100, verbose_name=b'\xd0\x9c\xd0\xb5\xd1\x81\xd1\x82\xd0\xbe \xd1\x83\xd1\x87\xd1\x91\xd0\xb1\xd1\x8b/\xd1\x80\xd0\xb0\xd0\xb1\xd0\xbe\xd1\x82\xd1\x8b', blank=True),
            preserve_default=True,
        ),
    ]
