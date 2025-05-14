import json
import logging
from rest_framework import status
from django.http import HttpResponse
from app_backend import serializers, models
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist
from no_code_testing_app_server.shared import BaseModelViewSet
from app_user_auth.auth_decorators.decorators import has_permission
from app_user_auth.utils.auth_utils import handle_reset_password_request, handle_new_user_creation

logger = logging.getLogger('no_code_testing_app')
CONTENT_TYPE = 'application/json'


class UserModelViewSet(BaseModelViewSet):
    serializer_class = serializers.AppUserSerializer
    queryset = models.User.objects.all()

    filterset_fields = ["user__is_active",]
    search_fields = ["$user__username",
                     "$user__email", "$first_name", "$last_name"]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return serializers.AppUserSerializer
        return serializers.CreateUpdateUserSerializer

    @has_permission("can_view_all_user")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @has_permission("can_create_user")
    def create(self, request, *args, **kwargs):
        try:
            user = serializers.CreateUpdateUserSerializer(
                data=request.data, context={'request': request})
            user.is_valid(raise_exception=True)
            user = user.save()
            handle_new_user_creation(user.user)
            return HttpResponse(status=status.HTTP_201_CREATED, content_type=CONTENT_TYPE)
        except ValidationError as v:
            logger.exception(str(v))
            return HttpResponse(json.dumps(v.__dict__), status=status.HTTP_422_UNPROCESSABLE_ENTITY, content_type=CONTENT_TYPE)
        except Exception as e:
            logger.exception(str(e))
            return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, content_type=CONTENT_TYPE)

    @has_permission("can_change_user")
    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            user = serializers.CreateUpdateUserSerializer(
                instance, data=request.data, partial=partial)
            user = user.update(instance=instance, validated_data=request.data)
            return HttpResponse(status=status.HTTP_200_OK, content=json.dumps(serializers.AppUserSerializer(user).data), content_type=CONTENT_TYPE)
        except ValidationError as v:
            logger.exception(str(v))
            return HttpResponse(json.dumps(v.__dict__), status=status.HTTP_422_UNPROCESSABLE_ENTITY, content_type=CONTENT_TYPE)
        except Exception as e:
            logger.exception(str(e))
            return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, content_type=CONTENT_TYPE)

    @has_permission("can_delete_user")
    def destroy(self, request, pk=None, *args, **kwargs):
        if int(pk) == int(request.app_user.id):
            return HttpResponse(status=status.HTTP_409_CONFLICT, content_type=CONTENT_TYPE)
        else:
            return super().destroy(request, *args, **kwargs)

    @has_permission("can_view_user")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @has_permission("can_change_user")
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @has_permission("can_change_user")
    @action(url_path='request-change-user-password', url_name='request-change-user-password', detail=True, methods=['GET'])
    def requestUserChangePassword(self, request, pk=None, *args, **kwargs):
        try:
            user = models.User.objects.get(id=pk)
            handle_reset_password_request(user.user)
            return HttpResponse(status=status.HTTP_201_CREATED, content_type=CONTENT_TYPE)
        except ObjectDoesNotExist as e:
            logger.exception(str(e))
            return HttpResponse(status=status.HTTP_404_NOT_FOUND, content_type=CONTENT_TYPE)
        except Exception as e:
            logger.exception(str(e))
            return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR, content_type=CONTENT_TYPE)

    # change password
    # update self user
