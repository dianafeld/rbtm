# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0007_auto_20150910_1604'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tomograph',
            name='angle',
        ),
        migrations.RemoveField(
            model_name='tomograph',
            name='current',
        ),
        migrations.RemoveField(
            model_name='tomograph',
            name='horizontal_shift',
        ),
        migrations.RemoveField(
            model_name='tomograph',
            name='shutter',
        ),
        migrations.RemoveField(
            model_name='tomograph',
            name='vertical_shift',
        ),
        migrations.RemoveField(
            model_name='tomograph',
            name='voltage',
        ),
        migrations.AlterField(
            model_name='tomograph',
            name='state',
            field=models.CharField(default=b'unavailable', max_length=12, choices=[(b'unavailable', b'unavailable'), (b'ready', b'ready'), (b'experiment', b'experiment')]),
            preserve_default=True,
        ),
    ]
