import logging
from rest_framework.viewsets import ReadOnlyModelViewSet
from . import serializers
from rest_framework.permissions import IsAuthenticated
from app_backend import models
from app_user_auth.auth_decorators.decorators import has_permission
logger = logging.getLogger('no_code_testing_app')


class PermissionViewSet(ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.AppPermissionSerializer
    queryset = models.AppPermission.objects.all()

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
