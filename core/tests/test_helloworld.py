from rest_framework.test import APIClient
from rest_framework import status
from django.conf import settings



class TestHelloWorld:
    def test_hello_world_success(self, api_client):
        response = api_client.get("/api/v1/hello_world")
           
        assert response.status_code == status.HTTP_200_OK
        