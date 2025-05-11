import logging
from workflow_builder_config_app import models
from rest_framework import serializers

logger = logging.getLogger('no_code_testing_app')


class BaseProviderSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Provider
        fields = '__all__'


class KwargSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Kwarg
        fields = '__all__'


class ComponentSerializer(serializers.ModelSerializer):
    extra_arguments = KwargSerializer(many=True, read_only=True)
    default_arguments = KwargSerializer(many=True, read_only=True)

    class Meta:
        model = models.Component
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    components = ComponentSerializer(many=True, read_only=True)

    class Meta:
        model = models.Category
        fields = '__all__'


class DependencySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Dependency
        fields = '__all__'


class ProviderSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    dependencies = DependencySerializer(many=True, read_only=True)

    class Meta:
        model = models.Provider
        fields = '__all__'
