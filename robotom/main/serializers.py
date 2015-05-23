from rest_framework import serializers
from models import UserProfile, RoleRequest


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('user', 'full_name', 'role', 'gender', 'phone_number', 'address', 'work_place',
                  'degree', 'title')


class RoleRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoleRequest
        fields = ('user', 'role', 'comment')
