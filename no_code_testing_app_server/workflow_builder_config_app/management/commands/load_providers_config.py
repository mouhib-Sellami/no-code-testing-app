import json
import os
from django.core.management.base import BaseCommand
from django.apps import apps
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Load workflow builder configuration from providers.json'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Start exporting data'))

        folder_path = os.path.join(
            os.getcwd(), 'workflow_builder_config_app', "providers-config")
        file_path = os.path.join(folder_path, 'providers.json')
        print(file_path)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"{file_path} does not exist")

        with open(file_path, 'r') as f:
            serialized_data = json.load(f)

        created_objects = {}

        for data in serialized_data:
            model_label = data['model']
            app_label, model_name = model_label.split('.')
            model = apps.get_model(app_label, model_name)
            fields = data['fields']
            pk = data['pk']

            m2m_fields = {k: v for k,
                          v in fields.items() if isinstance(v, list)}
            for key in m2m_fields:
                fields.pop(key)

            try:
                instance, created = model.objects.update_or_create(
                    pk=pk,
                    defaults=fields
                )
                action = "Created" if created else "Updated"
                self.stdout.write(f"{action} {model_label} with pk={pk}")
                created_objects[(model_label, pk)] = (instance, m2m_fields)
            except Exception as e:
                self.stderr.write(
                    f"Failed to process {model_label} with pk={pk}: {e}")
                continue

        for (model_label, pk), (instance, m2m_fields) in created_objects.items():
            for field_name, related_pks in m2m_fields.items():
                try:
                    related_manager = getattr(instance, field_name)
                    rel_model = related_manager.model
                    related_objects = rel_model.objects.filter(
                        pk__in=related_pks)
                    related_manager.set(related_objects)
                    self.stdout.write(
                        f"Set M2M {field_name} on {model_label} pk={pk}")
                except Exception as e:
                    self.stderr.write(
                        f"Failed to set M2M field '{field_name}' on {model_label} pk={pk}: {e}")

        self.stdout.write(self.style.SUCCESS(
            "Workflow data loaded successfully."))
