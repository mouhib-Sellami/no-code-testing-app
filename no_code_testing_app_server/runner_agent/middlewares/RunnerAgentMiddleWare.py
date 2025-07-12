from no_code_testing_app_server.auth.BearerTokenAuth import BearerTokenAuth
from django.http import HttpResponse
from runner_agent import models
from django.core.exceptions import ObjectDoesNotExist
from app_tenant import models as TENANT_MODELS

CONTENT_TYPE = "application/json"
INCLUDE_VIEW_SET = ["RunnerActionViewSet"]


class RunnerAgentMiddleWare:
    def __init__(self, get_response):
        self.get_response = get_response

    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.path.startswith('/api') and view_func.__name__ in INCLUDE_VIEW_SET:
            auth_token_meta = request.META.get('HTTP_AUTH_TOKEN')
            agent_key_meta = request.META.get('HTTP_AGENT_KEY')
            domain = request.META.get('HTTP_HOST')
            if auth_token_meta is None or agent_key_meta is None:
                return HttpResponse(status=403)

            try:
                agent = models.RunnerAgent.objects.filter(
                    agent_key=agent_key_meta, auth_token=auth_token_meta).first()
                if agent is None:
                    return HttpResponse(status=400)

                setattr(request, 'runner_agent', agent)

                try:
                    tenant = TENANT_MODELS.Tenant.objects.prefetch_related('domain_set').get(
                        domain_set__domain=domain)
                    setattr(request, 'tenant', tenant)
                except ObjectDoesNotExist:
                    return HttpResponse(status=400, content="Invalid tenant domain")

            except Exception as e:
                return HttpResponse(status=500, content=f"Server error: {str(e)}")

        return None

    def __call__(self, request):
        return self.get_response(request)
