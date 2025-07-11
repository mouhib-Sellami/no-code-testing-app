from workflow_builder_config_app import models
from no_code_testing_app_server.shared import DynamicModelSerializer


class BaseProviderSerializer(DynamicModelSerializer):

    class Meta:
        model = models.Provider
        fields = '__all__'


class KwargSerializer(DynamicModelSerializer):

    class Meta:
        model = models.Kwarg
        fields = '__all__'


class ComponentSerializer(DynamicModelSerializer):
    extra_arguments = KwargSerializer(many=True, read_only=True)
    default_arguments = KwargSerializer(many=True, read_only=True)

    class Meta:
        model = models.Component
        fields = '__all__'


class CategorySerializer(DynamicModelSerializer):
    components = ComponentSerializer(many=True, read_only=True)

    class Meta:
        model = models.Category
        fields = '__all__'


class DependencySerializer(DynamicModelSerializer):

    class Meta:
        model = models.Dependency
        fields = '__all__'


class ProviderSerializer(DynamicModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    dependencies = DependencySerializer(many=True, read_only=True)

    class Meta:
        model = models.Provider
        fields = '__all__'
