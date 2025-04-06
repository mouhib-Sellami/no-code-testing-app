from tenant_users.tenants.middleware import TenantAccessMiddleware
import re


class TenantAccessMiddleware(TenantAccessMiddleware):
    
    def __call__(self, request):
        if re.search(r'auth', request.path):
            return self.get_response(request)
        return super().__call__(request)
