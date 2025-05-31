from django.db import migrations
from no_code_testing_app_server.utils.generatePermissions import generate_permissions


def create_base_roles(apps, schema_editor):
    Role = apps.get_model('app_backend', 'OrgRole')
    Permission = apps.get_model('app_backend', 'AppPermission')
    agent_permissions = generate_permissions(['runner_agent'], Permission)

    admin_role = Role.objects.get(
        name='Admin',
    )
    owner_role = Role.objects.get(
        name='Owner',
    )
    staff = Role.objects.get(
        name='Staff',
    )
    for permission in agent_permissions:
        admin_role.permissions.add(permission)
        owner_role.permissions.add(permission)
        if 'VIEW' in permission.label and 'RUNNER_AGENT' in permission.label:
            staff.permissions.add(permission)


def reverse_create_base_roles(apps, schema_editor):
    Permission = apps.get_model('app_backend', 'AppPermission')
    agent_permissions = Permission.objects.filter(
        name__contains='runner_agent')
    agent_permissions.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('app_backend', '0016_componentdependency'),
    ]

    operations = [
        migrations.RunPython(
            code=create_base_roles,
            reverse_code=reverse_create_base_roles,
        ),
    ]
