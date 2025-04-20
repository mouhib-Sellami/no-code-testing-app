import logging
from rest_framework import status
from django.http import HttpResponse
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import AllowAny
from django_tenants.utils import schema_context, get_public_schema_name

logger = logging.getLogger('no_code_testing_app')
CONTENT_TYPE = 'application/json'


class DomainViewSet(GenericViewSet):
    permission_classes = [AllowAny]

    @schema_context(get_public_schema_name())
    @action(detail=False, url_name='retrieve', url_path='retrieve', methods=['GET'])
    def check_domain(self, request, *args, **kwargs):
        return HttpResponse(
            status=status.HTTP_200_OK,
            content_type=CONTENT_TYPE,
        )
