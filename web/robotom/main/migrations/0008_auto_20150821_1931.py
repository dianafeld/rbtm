# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_userprofile_activation_key'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='role',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='is_admin',
            field=models.BooleanField(default=b'False', verbose_name=b'\xd0\x90\xd0\xb4\xd0\xbc\xd0\xb8\xd0\xbd'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='userprofile',
            name='is_experimentator',
            field=models.BooleanField(default=b'False', verbose_name=b'\xd0\xad\xd0\xba\xd1\x81\xd0\xbf\xd0\xb5\xd1\x80\xd0\xb8\xd0\xbc\xd0\xb5\xd0\xbd\xd1\x82\xd0\xb0\xd1\x82\xd0\xbe\xd1\x80'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='userprofile',
            name='is_guest',
            field=models.BooleanField(default=b'True', verbose_name=b'\xd0\x93\xd0\xbe\xd1\x81\xd1\x82\xd1\x8c'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='userprofile',
            name='is_researcher',
            field=models.BooleanField(default=b'False', verbose_name=b'\xd0\x98\xd1\x81\xd1\x81\xd0\xbb\xd0\xb5\xd0\xb4\xd0\xbe\xd0\xb2\xd0\xb0\xd1\x82\xd0\xb5\xd0\xbb\xd1\x8c'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='rolerequest',
            name='user',
            field=models.ForeignKey(to='main.UserProfile'),
            preserve_default=True,
        ),
    ]
