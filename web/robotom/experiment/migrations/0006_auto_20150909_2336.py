# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0005_auto_20150909_1216'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tomograph',
            name='angle',
            field=models.FloatField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tomograph',
            name='exposure',
            field=models.FloatField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tomograph',
            name='horizontal_shift',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tomograph',
            name='vertical_shift',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
