# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_rolerequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='rolerequest',
            name='user',
            field=models.OneToOneField(default=1, to='main.UserProfile'),
            preserve_default=False,
        ),
    ]
