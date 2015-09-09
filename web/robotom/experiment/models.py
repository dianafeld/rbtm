# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User

TOMO_STATES = (
    ('off', 'off'),
    ('waiting', 'waiting'),
    ('experiment', 'experiment'),
    ('adjustment', 'adjustment'),
)

SHUTTER_STATES = (
    ('open', 'open'),
    ('closed', 'closed'),
)

class Tomograph(models.Model):
    state = models.CharField(max_length=15, default='off', choices=TOMO_STATES)
    voltage = models.FloatField(null=True, blank=True)
    current = models.FloatField(null=True, blank=True)
    shutter = models.CharField(max_length=6, default='closed', choices=SHUTTER_STATES, null=True, blank=True)
    angle = models.FloatField(null=True, blank=True)
    exposure = models.FloatField(null=True, blank=True)
    horizontal_shift = models.IntegerField(null=True, blank=True)
    vertical_shift = models.IntegerField(null=True, blank=True)