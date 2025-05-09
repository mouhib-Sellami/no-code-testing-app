from app_user_auth.viewSets import serializers as appBackendSerializer


def formateUserObject(user):
    return {
        'user': appBackendSerializer.BaseUserSerializer(user, context={'exclude_fields': ['organization']}).data,
        'role': appBackendSerializer.UserSerializer(user).data.get('role'),
        'organization': appBackendSerializer.UserSerializer(user).data.get('organization')
    }
