from rest_framework import filters
from .ViewSetsPagination import CustomPaginator
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from no_code_testing_app_server.auth.BearerTokenAuth import BearerTokenAuth


class BaseModelViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPaginator
    authentication_classes = [BearerTokenAuth]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
