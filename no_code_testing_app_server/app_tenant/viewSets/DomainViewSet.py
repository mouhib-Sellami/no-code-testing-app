import logging
from rest_framework import status
from django.http import HttpResponse
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet


logger = logging.getLogger('no_code_testing_app')
CONTENT_TYPE = 'application/json'


class DomainViewSet(GenericViewSet):

    @action(detail=False, url_name='retrieve', url_path='retrieve',methods=['GET'])
    def check_domain(self, request, *args, **kwargs):
        return HttpResponse(
            status=status.HTTP_200_OK,
            content_type=CONTENT_TYPE,
        )
