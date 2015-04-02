# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_auto_20150402_2028'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rolerequest',
            name='role',
            field=models.CharField(default=b'NONE', max_length=15, verbose_name=b'\xd0\x97\xd0\xb0\xd0\xbf\xd1\x80\xd0\xbe\xd1\x81 \xd0\xbd\xd0\xb0 \xd0\xb8\xd0\xb7\xd0\xbc\xd0\xb5\xd0\xbd\xd0\xb5\xd0\xbd\xd0\xb8\xd0\xb5 \xd1\x80\xd0\xbe\xd0\xbb\xd0\xb8', choices=[(b'NONE', b'-----'), (b'ADM', '\u0410\u0434\u043c\u0438\u043d'), (b'EXP', '\u042d\u043a\u0441\u043f\u0435\u0440\u0438\u043c\u0435\u043d\u0442\u0430\u0442\u043e\u0440'), (b'RES', '\u0418\u0441\u0441\u043b\u0435\u0434\u043e\u0432\u0430\u0442\u0435\u043b\u044c')]),
            preserve_default=True,
        ),
    ]
