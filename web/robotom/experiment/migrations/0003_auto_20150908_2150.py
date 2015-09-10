# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0002_auto_20150521_1023'),
    ]

    operations = [
        migrations.AddField(
            model_name='tomograph',
            name='angle',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tomograph',
            name='current',
            field=models.FloatField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tomograph',
            name='exposure',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tomograph',
            name='horizontal_shift',
            field=models.FloatField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tomograph',
            name='shutter',
            field=models.CharField(default=b'closed', max_length=6, choices=[(b'open', b'open'), (b'closed', b'closed')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tomograph',
            name='vertical_shift',
            field=models.FloatField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tomograph',
            name='voltage',
            field=models.FloatField(default=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tomograph',
            name='state',
            field=models.CharField(default=b'off', max_length=15, choices=[(b'off', b'off'), (b'waiting', b'waiting'), (b'experiment', b'experiment'), (b'adjustment', b'adjustment')]),
            preserve_default=True,
        ),
    ]
