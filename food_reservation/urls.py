from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('organizations',views.OrganizationViewSet,'organization')
router.register('client',views.ClientViewSet,'client')
router.register('buffet',views.BuffetViewSet,'buffet')


urlpatterns = [
    
] + router.urls