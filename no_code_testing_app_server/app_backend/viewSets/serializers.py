from rest_framework import serializers
from app_backend import models
from app_user_auth.viewSets import serializers as UserSerializers


class ProjectSerializer(serializers.ModelSerializer):
    user = UserSerializers.BaseUserSerializer()

    class Meta:
        model = models.Project
        fields = '__all__'
