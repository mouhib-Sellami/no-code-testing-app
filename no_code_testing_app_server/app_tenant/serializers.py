from rest_framework import serializers
from app_tenant import models


class BaseDomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Domain
        fields = '__all__'


class TenantSerializer(serializers.ModelSerializer):
    domain = serializers.SerializerMethodField('get_domain')

    class Meta:
        model = models.Tenant
        fields = '__all__'

    def get_domain(self, obj):
        domain = obj.domain_set.all().first()
        if domain:
            return BaseDomainSerializer(domain).data
        return None


class DomainSerializer(serializers.ModelSerializer):
    tenant = TenantSerializer()

    class Meta:
        model = models.Domain
        fields = '__all__'
