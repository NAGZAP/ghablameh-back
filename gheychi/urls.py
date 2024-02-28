from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
   openapi.Info(
      title="Gheychi API",
      default_version='v1',
      description="The Gheychi API from NAGZAP Group \n from IUST university",
      terms_of_service="https://gheychi.fiust.ir",
      contact=openapi.Contact(email="amirali.dst.lll@gmail.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('raamfar/', admin.site.urls),
    path('',include('core.urls')),
]\
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)\
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
