import json
import logging
from app_user_auth import models
from rest_framework import status
from django.http import HttpResponse
from app_user_auth import serializers
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.viewsets import GenericViewSet
from django.contrib.auth import authenticate, login, logout
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import IsAuthenticated
from django_tenants.utils import schema_context, get_public_schema_name, tenant_context
from no_code_testing_app_server.utils.userFormatter import formateUserObject
from no_code_testing_app_server.utils import verify_token_expiration
from app_user_auth.utils.auth_utils import handle_reset_password_request
from app_tenant import models as TENANT_MODELS
from runner_agent import models as AGENT_MODELS
import os
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
                # login(request, user)
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
            # login(request, user)
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
            logout(request)
            request.session.flush()
            request.auth.delete()
        except Exception as e:
            logger.exception(str(e))
        finally:
            return HttpResponse(status=status.HTTP_204_NO_CONTENT, content_type=CONTENT_TYPE)

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
            serializer = serializers.ForgetPasswordRequestSerializer(
                data=request.data)
            serializer.is_valid(raise_exception=True)

            email = serializer.validated_data['email']
            user = models.TenantUser.objects.get(
                email=email)
            handle_reset_password_request(user)
        except ValidationError as v:
            logger.exception(str(v))
            return HttpResponse(json.dumps(v.__dict__), status=status.HTTP_422_UNPROCESSABLE_ENTITY, content_type=CONTENT_TYPE)
        except ObjectDoesNotExist:
            pass
        except Exception as e:
            logger.exception(str(e))
            return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, content_type=CONTENT_TYPE)

        return HttpResponse(status=status.HTTP_201_CREATED, content_type=CONTENT_TYPE)

    @schema_context(get_public_schema_name())
    @action(detail=False, url_path='token/verify', methods=['POST'])
    def verify_token(self, request):
        try:
            check = verify_token_expiration(request.data['token'])
            if check:
                return HttpResponse(status=status.HTTP_400_BAD_REQUEST, content_type=CONTENT_TYPE)
            else:
                models.TenantUser.objects.get(
                    reset_token=request.data['token'])
            return HttpResponse(status=status.HTTP_202_ACCEPTED, content_type=CONTENT_TYPE)
        except ObjectDoesNotExist:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND, content_type=CONTENT_TYPE)
        except Exception as e:
            logger.exception(str(e))
            return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, content_type=CONTENT_TYPE)

    @schema_context(get_public_schema_name())
    @action(detail=False, url_path='reset/password', methods=['POST'], serializer_class=serializers.PasswordResetSerializer)
    def reset_password(self, request):
        try:
            serializer = serializers.PasswordResetSerializer(
                data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except ValidationError as v:
            logger.exception(str(v))
            return HttpResponse(json.dumps(v.__dict__), status=status.HTTP_422_UNPROCESSABLE_ENTITY, content_type=CONTENT_TYPE)
        except Exception as e:
            logger.exception(str(e))
            return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, content_type=CONTENT_TYPE)

        return HttpResponse(status=status.HTTP_201_CREATED, content_type=CONTENT_TYPE)

    @action(detail=False, url_path='emqx', url_name='emqx', methods=['POST'], serializer_class=serializers.UserLoginSerializer)
    def emqx(self, request):
        if os.environ['EMQX_DEFAULT_USERNAME'] == request.data['username'] and os.environ['EMQX_DEFAULT_PASSWORD'] == request.data['password']:
            return HttpResponse(json.dumps({'result': "allow"}), status=200, content_type=CONTENT_TYPE)
        else:
            tenant = TENANT_MODELS.Tenant.objects.get(
                id=request.data['client_id'])
            with tenant_context(tenant):
                try:
                    agent = AGENT_MODELS.RunnerAgent.objects.get(
                        agent_key=request.data['username'], auth_token=request.data['password'])
                    return HttpResponse(json.dumps({'result': "allow"}), status=200, content_type=CONTENT_TYPE)
                except AGENT_MODELS.RunnerAgent.DoesNotExist:
                    return HttpResponse(json.dumps({'result': "deny"}), status=200, content_type=CONTENT_TYPE)
                except Exception as e:
                    return HttpResponse(json.dumps({'result': "ignore"}), status=200, content_type=CONTENT_TYPE)
