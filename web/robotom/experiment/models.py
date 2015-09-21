# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User

TOMO_STATES = (
    ('off', 'off'),
    ('waiting', 'waiting'),
    ('experiment', 'experiment'),
    ('adjustment', 'adjustment'),
)

class Tomograph(models.Model):
    state = models.CharField(max_length=15, default='off', choices=TOMO_STATES)
