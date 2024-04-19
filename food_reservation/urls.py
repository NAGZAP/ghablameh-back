from django.urls import path
from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()
router.register('organizations',views.OrganizationViewSet,'organization')
router.register('clients',views.ClientViewSet,'client')
router.register('buffets',views.BuffetViewSet,'buffet')
router.register('clients/join-requests',views.ClientMembershipRequestViewSet,'client-join-requests')
router.register('organizations/join-requests',views.OrgMembershipRequestViewSet,'organization-join-requests')



urlpatterns = router.urls