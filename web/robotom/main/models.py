# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User

USER_ROLES = (
    ('ADM', u'Админ'),
    ('EXP', u'Экспериментатор'),
    ('RES', u'Исследователь'),
    ('GST', u'Гость'),
)

USER_GENDERS = (
    ('F', 'Женский'),
    ('M', 'Мужской'),
    ('N', 'Не указан')
)

USER_REQUESTS = (
    ('NONE', '-----'),
    ('ADM', u'Админ'),
    ('EXP', u'Экспериментатор'),
    ('RES', u'Исследователь'),
)


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    full_name = models.CharField('ФИО', max_length=100, blank=False)
    
    is_guest = models.BooleanField('Гость', default=True)
    is_admin = models.BooleanField('Админ', default=False)
    is_experimentator = models.BooleanField('Экспериментатор', default=False)
    is_researcher = models.BooleanField('Исследователь', default=False)
   
    gender = models.CharField('Пол', max_length=6, choices=USER_GENDERS, default='N')
    phone_number = models.CharField('Телефон', max_length=20, blank=True)
    address = models.CharField('Адрес', max_length=100, blank=True)
    work_place = models.CharField('Место учёбы/работы', max_length=100, blank=True)
    degree = models.CharField('Ученая степень', max_length=50, blank=True)
    title = models.CharField('Звание', max_length=50, blank=True)
    activation_key = models.CharField('Ключ активации', max_length=50, blank=True)

    def get_roles(self):
        if self.is_guest:
            return [u'Гость']
        roles = []
        if self.is_admin:
            roles.append(u'Админ')
        if self.is_experimentator:
            roles.append(u'Экспериментатор')
        if self.is_researcher:
            roles.append(u'Исследователь') 
        return roles 

    '''
    short role name, for example, 'RES' or 'ADM'
    '''
    def has_role(self, role):
        if role == 'NONE':
            return False
        return USER_ROLES[[role_tuple[0] for role_tuple in USER_ROLES].index(role)][1] in self.get_roles()

    '''
    long role name, for example, 'Исследователь'
    '''
    def has_role_long(self, role):
        return role in self.get_roles()

    def get_requests(self):
        return RoleRequest.objects.filter(user__pk=self.pk).exclude(role="NONE")

    def get_requested_roles(self):
        return [request.get_role_display() for request in self.get_requests()]

class RoleRequest(models.Model):
    user = models.ForeignKey(UserProfile)
    role = models.CharField('Запрос на изменение роли', max_length=15, choices=USER_REQUESTS, default='NONE')
    comment = models.TextField('Комментарий', max_length=300, blank=True)
