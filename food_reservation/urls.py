from django.urls import path,include
from rest_framework_nested import routers
from rest_framework.routers import DefaultRouter
from . import views

router = routers.DefaultRouter()
router.register('organizations',views.OrganizationViewSet,'organization')
router.register('organizations/join-requests',views.OrgMembershipRequestViewSet,'organization-join-requests')
router.register('clients',views.ClientViewSet,'client')
router.register('clients/my-organizations',views.ClientOrganizationViewSet,'client-organizations')
router.register('clients/join-requests',views.ClientMembershipRequestViewSet,'client-join-requests')
router.register('organizations/join-requests',views.OrgMembershipRequestViewSet,'organization-join-requests')
router.register('organizations/all-org',views.AllOrgListViewSet,'organization-all')
router.register('reserve',views.ReserveViewSet,'reserving')
router.register('buffets',views.BuffetViewSet,'buffet')
router.register('reservs',views.ReservationViewSet,'reservs')

buffets_router = routers.NestedDefaultRouter(router,'buffets',lookup='buffet') 
buffets_router.register('rates',views.BuffetsRateViewSet,'rates')
buffets_router.register('menus',views.DailyMenuViewSet,basename='menu')
buffets_router.register('weekly-menus',views.WeeklyMenuViewSet,basename='weekly-menu')




urlpatterns =\
    router.urls + buffets_router.urls

