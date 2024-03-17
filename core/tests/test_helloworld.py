from rest_framework.test import APIClient
from rest_framework import status



class TestHelloWorld:
    def test_hello_world_success(self, api_client):
        response = api_client.get("/hello_world")
        
        assert response.status_code == status.HTTP_200_OK
        