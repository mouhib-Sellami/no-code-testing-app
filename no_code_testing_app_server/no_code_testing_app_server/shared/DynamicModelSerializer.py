from rest_framework import serializers


class DynamicModelSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        include_fields = kwargs.pop(
            'include_fields', None) or self.context.get('include_fields', None)
        exclude_fields = kwargs.pop(
            'exclude_fields', None) or self.context.get('exclude_fields', None)

        if include_fields is not None:
            allowed = set(include_fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)

        if exclude_fields is not None:
            for field_name in exclude_fields:
                self.fields.pop(field_name, None)
