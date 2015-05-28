# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User

USER_ROLES = (
    ('ADM', 'Админ'),
    ('EXP', 'Экспериментатор'),
    ('RES', 'Исследователь'),
    ('GST', 'Гость'),
)

USER_GENDERS = (
    ('F', 'Женский'),
    ('M', 'Мужской'),
    ('N', 'Не указан')
)

USER_REQUESTS = (
    ('NONE', '-----'),
    ('ADM', 'Админ'),
    ('EXP', 'Экспериментатор'),
    ('RES', 'Исследователь'),
)


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    full_name = models.CharField('ФИО', max_length=100, blank=False)
    role = models.CharField('Роль на сайте', max_length=15, choices=USER_ROLES, default='GST')
    gender = models.CharField('Пол', max_length=6, choices=USER_GENDERS, default='N')
    phone_number = models.CharField('Телефон', max_length=20, blank=True)
    address = models.CharField('Адрес', max_length=100, blank=True)
    work_place = models.CharField('Место учёбы/работы', max_length=100, blank=True)
    degree = models.CharField('Ученая степень', max_length=50, blank=True)
    title = models.CharField('Звание', max_length=50, blank=True)
    activation_key = models.CharField('Ключ активации', max_length=50, blank=True)


class RoleRequest(models.Model):
    user = models.OneToOneField(UserProfile)
    # active request for assigning the role, 'NONE' if no active requests
    role = models.CharField('Запрос на изменение роли', max_length=15, choices=USER_REQUESTS, default='NONE')
    comment = models.TextField('Комментарий', max_length=300, blank=True)
