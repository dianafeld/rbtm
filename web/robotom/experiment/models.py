# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User


class Tomograph(models.Model):
    state = models.CharField(max_length=15)
