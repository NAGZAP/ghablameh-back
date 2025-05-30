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
router.register('reserve',views.ReservationViewSet,'reserving')
router.register('buffets',views.BuffetViewSet,'buffet')
router.register('foods',views.FoodViewSet,'food')

buffets_router = routers.NestedDefaultRouter(router,'buffets',lookup='buffet') 
buffets_router.register('rates',views.BuffetsRateViewSet,'rates')
buffets_router.register('menus',views.DailyMenuViewSet,basename='menu')
buffets_router.register('weekly-menus',views.WeeklyMenuViewSet,basename='weekly-menu')

daily_menu_router = routers.NestedDefaultRouter(buffets_router,'menus',lookup='menu')
daily_menu_router.register('meals',views.MealViewSet,'meals')

meal_router = routers.NestedDefaultRouter(daily_menu_router,'meals',lookup='meal')
meal_router.register('items',views.MealFoodViewSet,'items')




urlpatterns = router.urls + buffets_router.urls + daily_menu_router.urls + meal_router.urls
    

