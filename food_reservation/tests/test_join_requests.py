from django.conf import settings
from rest_framework import status
from food_reservation.models import *
from django.contrib.auth import get_user_model,authenticate
from model_bakery import baker
import pytest

User = get_user_model()



@pytest.fixture
def base_url():
    return f"/api/v{settings.VERSION}/"

@pytest.fixture
def client():
    return baker.make(Client)

@pytest.fixture
def organization():
    return baker.make(Organization)


@pytest.mark.django_db
class TestGetClientJoinRequests:

    def test_if_anonymous_get_401(self,base_url,api_client):

        respone = api_client.get(base_url+"client/join-requests/")

        assert respone.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_ok_get_200(self,base_url,api_client,client):

        api_client.force_authenticate(client.user)

        respone = api_client.get(base_url+"client/join-requests/")

        assert respone.status_code == status.HTTP_200_OK

    def test_if_client_has_no_requests_get_empty_list(self,base_url,api_client,client):
            
            api_client.force_authenticate(client.user)
    
            respone = api_client.get(base_url+"client/join-requests/")
    
            assert respone.data == []

    def test_if_client_has_requests_get_list(self,base_url,api_client,client):
                
        api_client.force_authenticate(client.user)
        baker.make(OrganizationMemberShipRequest,client=client)

        respone = api_client.get(base_url+"client/join-requests/")

        assert len(respone.data) == 1


@pytest.mark.django_db
class TestRetriveClientJoinRequest:

    def test_if_anonymous_get_401(self,base_url,api_client):

        respone = api_client.get(base_url+"client/join-requests/1/")

        assert respone.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_request_does_not_exist_get_404(self,base_url,api_client,client):

        api_client.force_authenticate(client.user)

        respone = api_client.get(base_url+"client/join-requests/1/")

        assert respone.status_code == status.HTTP_404_NOT_FOUND

    def test_if_request_exists_get_200(self,base_url,api_client,client):

        api_client.force_authenticate(client.user)
        request = baker.make(OrganizationMemberShipRequest,client=client)

        respone = api_client.get(base_url+f"client/join-requests/{request.id}/")

        assert respone.status_code == status.HTTP_200_OK

    def test_if_request_exists_get_request(self,base_url,api_client,client):

        api_client.force_authenticate(client.user)
        request = baker.make(OrganizationMemberShipRequest,client=client)

        respone = api_client.get(base_url+f"client/join-requests/{request.id}/")

        assert respone.data['id'] == request.id


@pytest.mark.django_db
class TestCreateClientJoinRequest:

    def test_if_anonymous_get_401(self,base_url,api_client):

        respone = api_client.post(base_url+"client/join-requests/")

        assert respone.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_ok_get_201(self,base_url,api_client,client,organization):

        api_client.force_authenticate(client.user)

        data = {
            'organization':organization.id
        }

        respone = api_client.post(base_url+"client/join-requests/",data)

        assert respone.status_code == status.HTTP_201_CREATED


    def test_if_ok_get_request(self,base_url,api_client,client,organization):

        api_client.force_authenticate(client.user)

        data = {
            'organization':organization.id
        }

        respone = api_client.post(base_url+"client/join-requests/",data)

        assert respone.data['organization_name'] == organization.name

    def test_if_client_already_have_request_donot_create_new_request(self,base_url,api_client,client,organization):

        api_client.force_authenticate(client.user)

        data = {
            'organization':organization.id
        }

        api_client.post(base_url+"client/join-requests/",data)

        respone = api_client.post(base_url+"client/join-requests/",data)

        assert respone.status_code == status.HTTP_201_CREATED
        assert OrganizationMemberShipRequest.objects.count() == 1

#TODO complete the tests for the rest of the endpoints



    