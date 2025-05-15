from django.db import models
from no_code_testing_app_server.shared import BaseModel
from app_user_auth import models as authModels


class AppPermission(BaseModel):
    label = models.CharField(max_length=255, null=False,
                             blank=True, default="", unique=True)

    def __str__(self) -> str:
        return self.label


class OrgRole(BaseModel):
    name = models.CharField(max_length=255, default='', null=True, blank=True)
    slug = models.CharField(max_length=255, default='', null=True, blank=True)
    permissions = models.ManyToManyField(
        AppPermission, related_name='role_permission')
    active = models.BooleanField(default=True)
    can_delete = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name


class User(BaseModel):
    user = models.OneToOneField(
        authModels.TenantUser, on_delete=models.DO_NOTHING, related_name='app_user', null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=False)
    last_name = models.CharField(max_length=255, null=True, blank=False)
    profession = models.CharField(max_length=255, null=True, blank=False)
    role = models.ForeignKey(
        OrgRole, on_delete=models.CASCADE, related_name="role_org_member")

    def delete(self, *args, **kwargs):
        try:
            deleting = super().delete(*args, **kwargs)
            if self.user:
                authModels.TenantUser.objects.delete_user(self.user)
            else:
                print("No associated TenantUser found.")
            return deleting
        except Exception as e:
            print(f"Error deleting TenantUser: {e}")


class Status(models.TextChoices):
    INDREAMSCAPE = 'In Dreamscape ✨'
    LAUNCHPREP = 'Launch Preparation 🚀'
    GALACTICCRUISE = 'Galactic Cruise ☄️'
    ORBITALPAUSE = 'Orbital Pause ⏸️'
    STELLARFINALE = 'Stellar Finale 🌟'
    CRASHLANDING = 'Crash Landing 💥'
    LOSTINVOID = 'Lost in Void 🕳️'


class Project(BaseModel):

    name = models.CharField(max_length=255, blank=False, null=True)
    description = models.TextField(blank=False, null=True)
    members = models.ManyToManyField(
        User, related_name="user_projects", null=True, blank=True)
    provider = models.ForeignKey(
        'workflow_builder_config_app.Provider',
        related_name="provider_projects", on_delete=models.SET_NULL, null=True, blank=True)
    managed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="managed_projects")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.INDREAMSCAPE,
        blank=False,
        null=False
    )

    def __str__(self):
        return f"{self.name} ({self.status})"

    def set_status(self, new_status, failure_reason=None):

        if new_status not in self.Status.values:
            raise ValueError(f"Invalid status: {new_status}")

        old_status = self.status
        self.status = new_status
        self.save()

        ProjectStatusLog.objects.create(
            project=self,
            old_status=old_status,
            new_status=new_status,
            failure_reason=failure_reason if new_status == Status.CRASHLANDING else None
        )


class ProjectStatusLog(BaseModel):
    project = models.ForeignKey(
        Project, related_name="status_logs", on_delete=models.CASCADE)
    old_status = models.CharField(
        max_length=20, choices=Status.choices, null=True, blank=True)
    new_status = models.CharField(
        max_length=20, choices=Status.choices)
    failure_reason = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.project.name}"
