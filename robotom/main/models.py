from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):    
    user = models.OneToOneField(User)
    middlename = models.CharField('Middlename', max_length=50, blank=True)
    
    USER_ROLES = (
        ('ADM', 'Admin'),
        ('EXP', 'Experimentator'),
        ('RES', 'Researcher'),
        ('GST', 'Guest'),
    )
    
    USER_GENDERS = (
        ('F', 'Female'),
        ('M', 'Male'),
        ('N', 'Not stated')
    )
    role = models.CharField('User role', max_length=15, choices=USER_ROLES, default = 'GST')
    gender = models.CharField('Gender', max_length=6, choices=USER_GENDERS, default = 'N')
    phone_number = models.CharField('Phone', max_length=20, blank=True)
    address = models.CharField('Address', max_length=100, blank=True)
    work_place = models.CharField('Work/study place', max_length=100, blank=True)
    degree = models.CharField('Degree', max_length=50, blank=True)
    title = models.CharField('Academic title', max_length=50, blank=True)