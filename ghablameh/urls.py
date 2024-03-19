from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings
from .swagger import schema_view

VERSION = settings.VERSION


urlpatterns = [
    path(f'api/v{VERSION}/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path(f'api/v{VERSION}/raamfar', admin.site.urls),
    path(f'api/v{VERSION}',include('core.urls')),
]\
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)\
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
