# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tomograph',
            name='state',
            field=models.CharField(max_length=15),
            preserve_default=True,
        ),
    ]
