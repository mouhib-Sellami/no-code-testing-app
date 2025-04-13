from django.db import models
from no_code_testing_app_server.utils.BaseModel import BaseModel
from tenant_users.tenants.models import UserProfile, UserProfileManager


class UserManager(UserProfileManager):
    def create_superuser(self, username, email, password):
        user = self.create_user(
            username=username, email=email, password=password)
        user.is_admin = True
        user.is_superuser = True
        user.email = email
        user.is_verified = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class TenantUser(UserProfile, BaseModel):
    username = models.CharField(
        max_length=255, unique=True, blank=False, null=False)
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    is_superuser = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = UserManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return True