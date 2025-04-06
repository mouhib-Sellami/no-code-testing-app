import json
import logging
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from . import serializers
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from app_user_auth import models
from rest_framework.exceptions import ValidationError
from django_tenants.utils import schema_context, get_public_schema_name

logger = logging.getLogger('brain_morph')
CONTENT_TYPE = 'application/json'

class AuthViewSet(GenericViewSet):

    @schema_context(get_public_schema_name())
    @action(detail=False, methods=['POST'], url_path='login', serializer_class=serializers.UserLoginSerializer)
    def login_(self, request):
        try:
            user = authenticate(
                username=request.data['username'], password=request.data['password'])
            if user is not None and user.is_active:
                login(request, user)
                token = Token.objects.get_or_create(user=user)
                return HttpResponse(
                    json.dumps(
                        {
                            'token': token[0].key,
                            'user': serializers.BaseUserSerializer(user).data,
                            # 'permissions': serializers.AppPermissionSerializer(user.role.permissions.all(), many=True).data,

                        }
                    ),
                    status=status.HTTP_200_OK,
                    content_type=CONTENT_TYPE,
                )
            else:
                return HttpResponse(
                    json.dumps({'details': 'invalid login'}),
                    status=status.HTTP_400_BAD_REQUEST,
                    content_type=CONTENT_TYPE,
                )
        except Exception as e:
            logger.exception(str(e))
            return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, content_type=CONTENT_TYPE)

    # @action(detail=False, methods=['POST'])
    # def logout(self, request):
    #     try:
    #         if request.auth.delete():
    #             return HttpResponse(status=status.HTTP_204_NO_CONTENT, content_type=CONTENT_TYPE)
    #     except Exception as e:
    #         logger.exception(str(e))
    #         return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, content_type=CONTENT_TYPE)

    # @action(
    #     detail=False, methods=['GET'], url_path='retrieve', permission_classes=[IsAuthenticated]
    # )
    # def get_auth(self, request):
    #     try:
    #         return HttpResponse(
    #             json.dumps(
    #                 {
    #                     'token': request.auth.key,
    #                     'user': serializers.UserSerializer(request.user).data,
    #                     'permissions': serializers.AppPermissionSerializer(request.user.role.permissions.all(), many=True).data,

    #                 }
    #             ),
    #             status=status.HTTP_200_OK,
    #             content_type=CONTENT_TYPE,
    #         )
    #     except Exception as e:
    #         logger.exception(str(e))
    #         return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, content_type=CONTENT_TYPE)

    # @action(detail=False, url_path='find/email', methods=['POST'])
    # def find_email(self, request):
    #     try:
    #         user = models.User.objects.get(email=request.data['email'])
    #         user.reset_token = secrets.token_urlsafe()
    #         user.save(update_fields=['reset_token'])
    #         send_email(ForgetPassword(email=user.email,
    #                    first_name=user.first_name, token=user.reset_token))
    #         return HttpResponse(status=status.HTTP_201_CREATED, content_type=CONTENT_TYPE)
    #     except ObjectDoesNotExist:
    #         logger.exception(str(e))
    #         return HttpResponse(json.dumps({'details': 'not found'}), status=status.HTTP_404_NOT_FOUND, content_type=CONTENT_TYPE)
    #     except Exception as e:
    #         logger.exception(str(e))
    #         return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, content_type=CONTENT_TYPE)

    # @action(detail=False, url_path='reset/password', methods=['POST'])
    # def reset_password(self, request):
    #     try:
    #         user = models.User.objects.get(reset_token=request.data['token'])
    #         user.reset_token = ''
    #         user.set_password(request.data['password'])
    #         user.save(update_fields=['reset_token', 'password'])
    #         # send email for password reset successfully
    #         return HttpResponse(status=status.HTTP_200_OK, content_type=CONTENT_TYPE)
    #     except ObjectDoesNotExist as not_found:
    #         logger.exception(str(not_found))
    #         return HttpResponse(json.dumps({'details': 'not found'}), status=status.HTTP_404_NOT_FOUND, content_type=CONTENT_TYPE)
    #     except Exception as e:
    #         logger.exception(str(e))
    #         return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, content_type=CONTENT_TYPE)
