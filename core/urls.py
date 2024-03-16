from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register("auth",views.Authentication,basename="authentication")



urlpatterns = [
    path('hello_world/',views.hello_world)
] + router.urls