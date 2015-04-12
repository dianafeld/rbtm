# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_auto_20150405_1715'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='activation_key',
            field=models.CharField(max_length=50, verbose_name=b'\xd0\x9a\xd0\xbb\xd1\x8e\xd1\x87 \xd0\xb0\xd0\xba\xd1\x82\xd0\xb8\xd0\xb2\xd0\xb0\xd1\x86\xd0\xb8\xd0\xb8', blank=True),
            preserve_default=True,
        ),
    ]
