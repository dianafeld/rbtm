# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Tomograph',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('state', models.CharField(max_length=15, verbose_name=b'\xd1\x82\xd0\xb5\xd0\xba\xd1\x83\xd1\x89\xd0\xb5\xd0\xb5 \xd1\x81\xd0\xbe\xd1\x81\xd1\x82\xd0\xbe\xd1\x8f\xd0\xbd\xd0\xb8\xd0\xb5')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
