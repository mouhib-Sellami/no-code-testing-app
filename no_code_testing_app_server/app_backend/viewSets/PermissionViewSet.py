from app_backend import serializers, models
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated


class PermissionViewSet(ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.AppPermissionSerializer
    queryset = models.AppPermission.objects.all()

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
