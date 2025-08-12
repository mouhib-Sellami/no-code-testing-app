import secrets
import string
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django_tenants.utils import get_tenant_model, schema_context
import logging
import os

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--schema', type=str,
                            default='public', help='Tenant schema name')

    def generate_secure_password(self, length=16):
        """Generate a secure random password."""
        characters = string.ascii_letters + string.digits + string.punctuation
        return ''.join(secrets.choice(characters) for _ in range(length))

    def handle(self, *args, **options):
        logger.debug("Executing create_tenant_superuser command")
        username = os.getenv('APP_ROOT_USER')
        password = os.getenv('APP_ROOT_PASSWORD')
        email = os.getenv('APP_ROOT_EMAIL')
        schema_name = options['schema']

        if not password:
            password = self.generate_secure_password()
            self.stdout.write(self.style.NOTICE(
                f"Generated password for '{username}': {password}"))
            self.stdout.write(self.style.WARNING(
                "Please save this password securely, as it will not be shown again."))

        User = get_user_model()
        TenantModel = get_tenant_model()

        try:
            tenant = TenantModel.objects.get(schema_name=schema_name)
        except TenantModel.DoesNotExist:
            logger.error(f"Tenant with schema '{schema_name}' does not exist.")
            raise CommandError(
                f"Tenant with schema '{schema_name}' does not exist.")

        try:
            with schema_context(schema_name):
                if not User.objects.filter(username=username).exists():
                    user = User.objects.create_superuser(
                        username=username, password=password, email=email)
                    user.set_password(password)
                    user.save(update_fields=['password'])
                    self.stdout.write(self.style.SUCCESS(
                        f"Superuser '{username}' created on schema '{schema_name}'"
                    ))
                else:
                    self.stdout.write(self.style.WARNING(
                        f"Superuser '{username}' already exists on schema '{schema_name}'"
                    ))
        except Exception as e:
            logger.error(
                f"Error creating superuser on schema '{schema_name}': {str(e)}")
            raise CommandError(f"Error creating superuser: {str(e)}")
