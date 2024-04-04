from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.authentication import JWTAuthentication

schema_view = get_schema_view(
   openapi.Info(
      title="Ghablameh API",
      default_version='v1',
      description="The Ghablameh API from NAGZAP Group \n from IUST university",
      terms_of_service="https://Ghablameh.fiust.ir",
      contact=openapi.Contact(email="amirali.dst.lll@gmail.com"),
      license=openapi.License(name="BSD License"),
      x={
         'security': [{'Bearer': []}],
      },
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
   authentication_classes=(JWTAuthentication,),
)