from django.urls import path
from rest_framework_nested import routers
from rest_framework.routers import DefaultRouter
from . import views

router = routers.DefaultRouter()
router.register('organizations',views.OrganizationViewSet,'organization')
router.register('organizations/join-requests',views.OrgMembershipRequestViewSet,'organization-join-requests')
router.register('clients',views.ClientViewSet,'client')
router.register('clients/join-requests',views.ClientMembershipRequestViewSet,'client-join-requests')
router.register('buffets',views.BuffetViewSet,'buffet')
router.register('reservs',views.ReservationViewSet,'reservs')



buffets_router = routers.NestedDefaultRouter(router,'buffets',lookup='buffet') 
buffets_router.register('rates',views.BuffetsRateViewSet,'rates')


urlpatterns = router.urls + buffets_router.urls