from rest_framework import serializers
from app_tenant import models
from slugify import slugify


class BaseDomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Domain
        fields = '__all__'


class TenantSerializer(serializers.ModelSerializer):
    domain = serializers.SerializerMethodField('get_domain')

    class Meta:
        model = models.Tenant
        fields = ('id', 'name', 'slug', 'domain', 'created_at', 'updated_at')

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


class BaseTenantSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Tenant
        fields = '__all__'


class OrganizationSignUpSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=255, required=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = models.Tenant
        fields = ('name', 'email','org_pic')

    def validate_name(self, value):
        slug = slugify(value, allow_unicode=False)
        if models.Tenant.objects.filter(slug=slug).exists():
            raise serializers.ValidationError(
                "An organization with this name already exists.")
        return value

    def validate_email(self, value):
        if models.Tenant.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "An organization with this email already exists.")
        return value

    def validate(self, data):
        slug = slugify(data['name'], allow_unicode=False)
        schema_name = slug
        domain_name = slug.replace('-', '')

        if models.Tenant.objects.filter(schema_name=schema_name).exists():
            raise serializers.ValidationError(
                {"schema_name": "This schema name is already in use."})

        data['slug'] = slug
        data['schema_name'] = schema_name
        data['domain_name'] = domain_name + ".localhost"
        return data

    def create(self, validated_data):
        domain_name = validated_data.pop('domain_name')
        tenant = models.Tenant.objects.create(**validated_data)
        models.Domain.objects.create(
            tenant=tenant, domain=domain_name, is_primary=True)
        return tenant
