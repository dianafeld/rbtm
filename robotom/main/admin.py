from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group
from main.models import UserProfile

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False

class MyUserAdmin(UserAdmin):
    def user_role(self, obj):
        return obj.userprofile.role()
    user_role.short_description = 'User role'

    inlines = (UserProfileInline,)
    list_display = ['username', 'email', 'first_name', 'last_name', 'user_role', 'is_staff',]


admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)

