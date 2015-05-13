# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User

class Tomo(models.Model):
	condition = models.CharField(max_length = 1)

class Experiment(models.Model):
    exp_id = models.CharField(max_length = 100) 
    user = models.OneToOneField(User)
    
