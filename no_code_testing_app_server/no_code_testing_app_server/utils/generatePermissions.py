MODEL_ACTIONS = ["create", "view","view_all", "change", "delete"]


def generate_permissions(models, model):
    permissions = []
    for model_name in models:
        for action in MODEL_ACTIONS:
            permission = "can_" + action + "_" + model_name
            permission = permission.upper()
            permission_dict = {"label": permission}
            permissions.append(permission_dict)
            model.objects.update_or_create(
                defaults=permission_dict, **permission_dict)
    return model.objects.all()
