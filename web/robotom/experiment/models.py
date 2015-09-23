# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User

TOMO_STATES = (
    ('unavailable', 'unavailable'),
    ('ready', 'ready'),
    ('experiment', 'experiment'),
)

class Tomograph(models.Model):
    state = models.CharField(max_length=12, default='unavailable', choices=TOMO_STATES)
