import logging
from rest_framework.viewsets import ModelViewSet
from . import serializers
from rest_framework.permissions import IsAuthenticated
from app_backend import models
from app_user_auth.auth_decorators.decorators import has_permission
from app_backend.pagination_filters.app_pagination import defaultPagination
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend

logger = logging.getLogger('sky_forge')
CONTENT_TYPE = 'application/json'


class UserModelViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.AppBaseUserSerializer
    queryset = models.User.objects.all()

    pagination_class = defaultPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]

    filterset_fields = ["user__is_active",]
    search_fields = ["$user__username",
                     "$user__email", "$first_name", "$last_name"]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return serializers.AppUserSerializer
        return serializers.CreateUserSerializer

    @has_permission("can_view_all_user")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @has_permission("can_create_user")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @has_permission("can_change_user")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @has_permission("can_delete_user")
    def destroy(self, request, pk=None, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @has_permission("can_view_user")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @has_permission("can_change_user")
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
