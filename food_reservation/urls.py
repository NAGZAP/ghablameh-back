from django.urls import path
from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()
router.register('organizations',views.OrganizationViewSet,'organization')
router.register('client',views.ClientViewSet,'client')
router.register('buffet',views.BuffetViewSet,'buffet')
router.register('client/join-requests',views.ClientMembershipRequestViewSet,'client-join-requests')
router.register('organizations/join-requests',views.OrgMembershipRequestViewSet,'organization-join-requests')



urlpatterns = router.urls