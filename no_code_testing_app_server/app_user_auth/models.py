from django.db import models
from no_code_testing_app_server.utils.BaseModel import BaseModel
from tenant_users.tenants.models import AbstractBaseUser, UserProfileManager, UserProfile
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class UserManager(UserProfileManager):
    def create_superuser(self, username, email, password):
        user = self.create_user(
            username=username, email=email, password=password, is_staff=True)
        user.is_admin = True
        user.is_superuser = True
        user.email = email
        user.is_verified = True
        user.is_staff = True
        user.save(using=self._db)
        return user

    def delete_user(self, user_obj):
        user_obj.delete()


class TenantUser(AbstractBaseUser, BaseModel):
    username = models.CharField(
        max_length=255, unique=True, blank=False, null=False)

    tenants = models.ManyToManyField(settings.TENANT_MODEL, verbose_name=_(
        "tenants"), blank=True, help_text=_("The tenants this user belongs to."), related_name="user_set")

    email = models.EmailField(
        _("Email Address"),
        unique=True,
        db_index=True)

    is_active = models.BooleanField(_("active"), default=True)

    is_verified = models.BooleanField(_("verified"), default=False)
    is_superuser = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=True)
    reset_token = models.CharField(
        default='', max_length=255, null=True, blank=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = UserManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return True
