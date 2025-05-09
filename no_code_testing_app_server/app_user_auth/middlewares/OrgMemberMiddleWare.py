from no_code_testing_app_server.auth.BearerTokenAuth import BearerTokenAuth
from django.http import HttpResponse
CONTENT_TYPE = "application/json"

EXCLUDE_VIEW_FUNC = ["AuthViewSet", "DomainViewSet"]


class OrgMemberMiddleWare:
    def __init__(self, get_response):
        self.get_response = get_response

    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.path.startswith('/api') and view_func.__name__ not in EXCLUDE_VIEW_FUNC:
            try:
                user = BearerTokenAuth(
                ).authenticate(request=request)[0]
                if user and user.app_user:
                    setattr(request, "app_user",
                            user.app_user)
            except Exception as e:
                print(e)
                pass

    def __call__(self, request):
        return self.get_response(request)
