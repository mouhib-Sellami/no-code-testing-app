from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from no_code_testing_app_server.config.api_docs import urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('app_user_auth.urls')),
    path('api/', include('app_tenant.urls')),
    path('logs/', include('log_viewer.urls')),
    path('api/', include('workflow_builder_config_app.urls')),
]+urls+static(settings.STATIC_URL,
              document_root=settings.STATIC_ROOT)
