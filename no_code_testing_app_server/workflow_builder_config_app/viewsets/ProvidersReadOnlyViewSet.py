
import logging
from rest_framework.viewsets import ReadOnlyModelViewSet
from workflow_builder_config_app import serializers, models
from rest_framework.permissions import IsAuthenticated

logger = logging.getLogger('no_code_testing_app')


class ProvidersReadOnlyViewSet(ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.BaseProviderSerializer
    queryset = models.Provider.objects.all()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return serializers.ProviderSerializer
        return serializers.BaseProviderSerializer

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
