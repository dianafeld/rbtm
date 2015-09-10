# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0004_auto_20150909_1139'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tomograph',
            name='angle',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tomograph',
            name='current',
            field=models.FloatField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tomograph',
            name='exposure',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tomograph',
            name='horizontal_shift',
            field=models.FloatField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tomograph',
            name='shutter',
            field=models.CharField(default=b'closed', max_length=6, null=True, blank=True, choices=[(b'open', b'open'), (b'closed', b'closed')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tomograph',
            name='vertical_shift',
            field=models.FloatField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tomograph',
            name='voltage',
            field=models.FloatField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
