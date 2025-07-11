from app_backend import serializers, models
from rest_framework.viewsets import GenericViewSet, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
import logging
from app_backend import serializers, models

logger = logging.getLogger('no_code_testing_app')
CONTENT_TYPE = "application/json"


class ProjectComponentViewSet(GenericViewSet, mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, mixins.UpdateModelMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.ProjectComponentSerializer
    queryset = models.ProjectComponent.objects.all()

    def get_serializer_class(self):
        if self.action in ['create']:
            return serializers.CreateProjectComponentSerializer
        return serializers.ProjectComponentSerializer

    def destroy(self, request, *args, **kwargs):
        models.Kwarg.objects.filter(
            Q(project_component_extra_arguments_kwargs__id=kwargs['pk']) |
            Q(project_component_default_arguments_kwargs__id=kwargs['pk'])
        ).delete()
        return super().destroy(request, *args, **kwargs)
