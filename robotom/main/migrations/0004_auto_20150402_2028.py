# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_rolerequest_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rolerequest',
            name='comment',
            field=models.TextField(max_length=300, verbose_name=b'\xd0\x9a\xd0\xbe\xd0\xbc\xd0\xbc\xd0\xb5\xd0\xbd\xd1\x82\xd0\xb0\xd1\x80\xd0\xb8\xd0\xb9', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='role',
            field=models.CharField(default=b'GST', max_length=15, verbose_name=b'\xd0\xa0\xd0\xbe\xd0\xbb\xd1\x8c \xd0\xbd\xd0\xb0 \xd1\x81\xd0\xb0\xd0\xb9\xd1\x82\xd0\xb5', choices=[(b'ADM', '\u0410\u0434\u043c\u0438\u043d'), (b'EXP', '\u042d\u043a\u0441\u043f\u0435\u0440\u0438\u043c\u0435\u043d\u0442\u0430\u0442\u043e\u0440'), (b'RES', '\u0418\u0441\u0441\u043b\u0435\u0434\u043e\u0432\u0430\u0442\u0435\u043b\u044c'), (b'GST', '\u0413\u043e\u0441\u0442\u044c')]),
            preserve_default=True,
        ),
    ]
