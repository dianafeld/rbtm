# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RoleRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('comment', models.TextField(max_length=300, blank=True)),
                ('role', models.CharField(default=b'NONE', max_length=15, verbose_name=b'\xd0\x97\xd0\xb0\xd0\xbf\xd1\x80\xd0\xbe\xd1\x81 \xd0\xbd\xd0\xb0 \xd0\xb8\xd0\xb7\xd0\xbc\xd0\xb5\xd0\xbd\xd0\xb5\xd0\xbd\xd0\xb8\xd0\xb5 \xd1\x80\xd0\xbe\xd0\xbb\xd0\xb8', choices=[(b'NONE', b'-----'), (b'ADM', b'\xd0\x90\xd0\xb4\xd0\xbc\xd0\xb8\xd0\xbd'), (b'EXP', b'\xd0\xad\xd0\xba\xd1\x81\xd0\xbf\xd0\xb5\xd1\x80\xd0\xb8\xd0\xbc\xd0\xb5\xd0\xbd\xd1\x82\xd0\xb0\xd1\x82\xd0\xbe\xd1\x80'), (b'RES', b'\xd0\x98\xd1\x81\xd1\x81\xd0\xbb\xd0\xb5\xd0\xb4\xd0\xbe\xd0\xb2\xd0\xb0\xd1\x82\xd0\xb5\xd0\xbb\xd1\x8c')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
