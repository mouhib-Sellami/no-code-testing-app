
import json
from functools import wraps
from rest_framework import status
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
CONTENT_TYPE = 'application/json'

def has_permission(name: str):
    def inner_decorator(f):
        @wraps(f)
        def decorator(*args, **kwargs):
            """"""
            try:
                request = args[1]
                permissions = request.permissions
                permission = permissions.get(label=name.upper())
                return f(*args, **kwargs)
            except ObjectDoesNotExist as e:
                return HttpResponse(json.dumps({"details": "unauthorized"}), status=status.HTTP_403_FORBIDDEN, content_type=CONTENT_TYPE)
        return decorator
    return inner_decorator
