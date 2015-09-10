# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0006_auto_20150909_2336'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tomograph',
            name='exposure',
        ),
        migrations.AlterField(
            model_name='tomograph',
            name='shutter',
            field=models.CharField(default=b'closed', max_length=6, null=True, blank=True, choices=[(b'opened', b'opened'), (b'closed', b'closed')]),
            preserve_default=True,
        ),
    ]
