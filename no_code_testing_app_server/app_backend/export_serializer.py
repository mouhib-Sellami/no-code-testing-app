from app_backend import models
from no_code_testing_app_server.shared import DynamicModelSerializer


class AppPermissionSerializer(DynamicModelSerializer):
    class Meta:
        model = models.AppPermission
        fields = '__all__'


class OrgRoleReadSerializer(DynamicModelSerializer):
    permissions = AppPermissionSerializer(many=True)

    class Meta:
        model = models.OrgRole
        fields = '__all__'


class AppBaseUserSerializer(DynamicModelSerializer):

    class Meta:
        model = models.User
        fields = '__all__'

    def get_fields(self):
        fields = super().get_fields()
        exclude_fields = self.context.get("exclude_fields", [])
        for field in exclude_fields:
            fields.pop(field, default=None)
        return fields
