import json
import logging
import secrets
from . import serializers
from app_user_auth import models
from rest_framework import status
from django.http import HttpResponse
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.viewsets import GenericViewSet
from django.contrib.auth import authenticate, login
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import IsAuthenticated
from django_tenants.utils import schema_context, get_public_schema_name
from no_code_testing_app_server.utils.userFormatter import formateUserObject

logger = logging.getLogger('no_code_testing_app')
CONTENT_TYPE = 'application/json'


class AuthViewSet(GenericViewSet):
    permission_classes = [AllowAny]

    @schema_context(get_public_schema_name())
    @action(detail=False, methods=['POST'], url_path='login', serializer_class=serializers.UserLoginSerializer)
    def login_(self, request):
        try:
            user = authenticate(
                username=request.data['username'], password=request.data['password'])
            if user is not None and user.is_active:
                login(request, user)
                token = Token.objects.get_or_create(user=user)
                user_obj = formateUserObject(user)
                user_obj.update({'token': token[0].key})
                return HttpResponse(
                    json.dumps(
                        user_obj
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

    @schema_context(get_public_schema_name())
    @action(detail=False, methods=['POST'], url_path='signup', serializer_class=serializers.UserSignupViewSerializer)
    def signup_(self, request):
        try:
            user_data: dict = request.data
            user = serializers.UserSignupViewSerializer(data=user_data)
            user.is_valid(raise_exception=True)
            user: models.TenantUser = user.save()
            user.set_password(request.data['password'])
            user.save(update_fields=['password'])
            login(request, user)
            token = Token.objects.get_or_create(user=user)
            user_obj = formateUserObject(user)
            user_obj.update({'token': token[0].key})
            return HttpResponse(
                json.dumps(
                    user_obj
                ),
                status=status.HTTP_200_OK,
                content_type=CONTENT_TYPE,
            )
        except ValidationError as v:
            logger.exception(str(v))
            return HttpResponse(json.dumps(v.__dict__), status=status.HTTP_422_UNPROCESSABLE_ENTITY, content_type=CONTENT_TYPE)

        except Exception as e:
            logger.exception(str(e))
            return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, content_type=CONTENT_TYPE)

    @schema_context(get_public_schema_name())
    @action(detail=False, methods=['POST'])
    def logout(self, request):
        try:
            if request.auth.delete():
                return HttpResponse(status=status.HTTP_204_NO_CONTENT, content_type=CONTENT_TYPE)
        except Exception as e:
            logger.exception(str(e))
            return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, content_type=CONTENT_TYPE)

    @schema_context(get_public_schema_name())
    @action(
        detail=False, methods=['GET'], url_path='retrieve', permission_classes=[IsAuthenticated]
    )
    def get_auth(self, request):
        try:
            user_obj = formateUserObject(request.user)
            user_obj.update({'token': request.auth.key})
            return HttpResponse(
                json.dumps(
                    user_obj
                ),
                status=status.HTTP_200_OK,
                content_type=CONTENT_TYPE,
            )
        except Exception as e:
            logger.exception(str(e))
            return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, content_type=CONTENT_TYPE)

    @schema_context(get_public_schema_name())
    @action(detail=False, url_path='find/email', methods=['POST'], serializer_class=serializers.ForgetPasswordRequestSerializer)
    def find_email(self, request):
        try:
            user = models.TenantUser.objects.get(email=request.data['email'])
            user.reset_token = secrets.token_urlsafe()
            user.save(update_fields=['reset_token'])
            # send_email(ForgetPassword(email=user.email,
            #            first_name=user.first_name, token=user.reset_token))
        except ObjectDoesNotExist:
            pass
            return HttpResponse(status=status.HTTP_201_CREATED, content_type=CONTENT_TYPE)
        except Exception as e:
            logger.exception(str(e))
            return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, content_type=CONTENT_TYPE)
