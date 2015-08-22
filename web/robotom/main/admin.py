# -*- coding: utf-8 -*-
from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group
from main.models import UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    exclude = ('first_name', 'last_name',)


class MyUserAdmin(UserAdmin):
    def user_role(self, obj):
        return ', '.join(obj.userprofile.get_roles())

    user_role.short_description = 'Роли на сайте'

    def full_name(self, obj):
        return obj.userprofile.full_name

    full_name.short_description = 'ФИО'

    inlines = (UserProfileInline,)
    list_display = ['username', 'email', 'full_name', 'user_role', 'is_staff', ]


admin.site.unregister(User)
admin.site.unregister(Group)

admin.site.register(User, MyUserAdmin)
