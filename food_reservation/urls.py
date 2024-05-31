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
router.register('foods',views.FoodViewSet,'list_of_foods')
router.register('reserve',views.ReserveViewSet,'reserving')

router.register('buffets',views.BuffetViewSet,'buffet')
router.register('reservs',views.ReservationViewSet,'reservs')
buffet_router = routers.NestedSimpleRouter(router,r'buffets',lookup='buffet')
buffet_router.register(r'menus',views.DailyMenuViewSet,basename='menu')


daily_router = routers.NestedSimpleRouter(buffet_router,r'menus',lookup='menu')
daily_router.register(r'meals',views.MealViewSet,basename='meal')



buffets_router = routers.NestedDefaultRouter(router,'buffets',lookup='buffet') 
buffets_router.register('rates',views.BuffetsRateViewSet,'rates')

meal_router = routers.NestedSimpleRouter(daily_router,r'meals',lookup='meal')
meal_router.register(r'meals',views.MealFoodViewSet,basename='food')


urlpatterns = [path(r'', include(router.urls)),
               path(r'', include(buffet_router.urls)),
                path(r'', include(daily_router.urls)),
                 path(r'', include(meal_router.urls)) ] #+ router.urls + buffets_router.urls

