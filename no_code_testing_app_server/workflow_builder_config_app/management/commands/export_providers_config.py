import json
import os
from django.core import serializers
from django.core.management.base import BaseCommand, CommandError
from django.apps import apps
from django.core.files import File
from uuid import uuid4
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS(f'Start exporting data'))
        models_to_handle = ['Kwarg', 'Component',
                            'Dependency', 'Category', 'Provider']
        data = []
        for model_name in models_to_handle:
            model = apps.get_model('workflow_builder_config_app', model_name)
            data.extend(serializers.serialize('python', model.objects.all()))
            
        serialized_data = []
        for item in data:
            serialized_item = {
                'model': item['model'],
                'pk': item['pk'],
                'fields': item['fields']
            }
            if item['model'] == 'your_app_name.Provider' and item['fields'].get('image'):
                with open(item['fields']['image'], 'rb') as f:
                    serialized_item['fields']['image'] = f.read().hex()
            serialized_data.append(serialized_item)
            
        output_folder = os.path.join(os.getcwd(),'workflow_builder_config_app', "providers-config")
        
        if not os.path.exists(output_folder):
            os.makedirs(output_folder, exist_ok=True)
            
        output_file = os.path.join(output_folder, 'providers.json')
        
        with open(output_file, 'w') as file:
            json.dump(serialized_data, file, indent=2, sort_keys=True, default=str)
        self.stdout.write(self.style.SUCCESS(f'Finish exporting data'))
