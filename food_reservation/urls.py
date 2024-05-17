from django.urls import path,include
from rest_framework_nested import routers

from . import views

router = routers.DefaultRouter()
router.register('organizations',views.OrganizationViewSet,'organization')
router.register('clients',views.ClientViewSet,'client')
router.register('buffets',views.BuffetViewSet,'buffet')
router.register('clients/join-requests',views.ClientMembershipRequestViewSet,'client-join-requests')
router.register('organizations/join-requests',views.OrgMembershipRequestViewSet,'organization-join-requests')
router.register('organizations/all-org',views.AllOrgListViewSet,'organization-all')
router.register('foods',views.FoodViewSet,'list_of_foods')
router.register('reserve',views.ReserveViewSet,'reserving')


buffet_router = routers.NestedSimpleRouter(router,r'buffets',lookup='buffet')
buffet_router.register(r'menus',views.DailyMenuViewSet,basename='menu')


daily_router = routers.NestedSimpleRouter(buffet_router,r'menus',lookup='menu')
daily_router.register(r'meals',views.MealViewSet,basename='meal')


meal_router = routers.NestedSimpleRouter(daily_router,r'meals',lookup='meal')
meal_router.register(r'meals',views.MealFoodViewSet,basename='food')

urlpatterns = [path(r'', include(router.urls)),
               path(r'', include(buffet_router.urls)),
                path(r'', include(daily_router.urls)),
                 path(r'', include(meal_router.urls)) ]