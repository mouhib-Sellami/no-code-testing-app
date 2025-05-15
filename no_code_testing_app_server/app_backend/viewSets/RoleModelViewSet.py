import logging
from rest_framework import status
from django.http import HttpResponse
from app_backend import serializers, models
from django.core.exceptions import ObjectDoesNotExist
from app_user_auth.auth_decorators.decorators import has_permission
from no_code_testing_app_server.shared import BaseModelViewSet

logger = logging.getLogger('no_code_testing_app')
CONTENT_TYPE = 'application/json'


class RoleModelViewSet(BaseModelViewSet):

    serializer_class = serializers.OrgRoleReadSerializer
    queryset = models.OrgRole.objects.all().order_by('created_at')

    search_fields = ["$name","$slug"]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return serializers.OrgRoleReadSerializer
        return serializers.OrgRoleCreateSerializer

    @has_permission("can_view_all_role")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @has_permission("can_create_role")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @has_permission("can_change_role")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @has_permission("can_delete_role")
    def destroy(self, request, *args, **kwargs):
        try:
            role = models.OrgRole.objects.get(pk=kwargs["pk"])
            if role.can_delete:
                return super().destroy(request, *args, **kwargs)
            else:
                return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content_type=CONTENT_TYPE)
        except ObjectDoesNotExist:
            return super().destroy(request, *args, **kwargs)

    @has_permission("can_view_role")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @has_permission("can_change_role")
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
