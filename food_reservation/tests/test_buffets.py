from django.conf import settings
from rest_framework import status
from food_reservation.models import *
from django.contrib.auth import get_user_model
from model_bakery import baker
import pytest

User = get_user_model()



@pytest.fixture
def base_buffets_url():
    return f"/api/v{settings.VERSION}/buffets/"


@pytest.mark.django_db
class TestBuffetsList:
    def test_if_anonymous_gets_401(self,api_client,base_buffets_url):
        response = api_client.get(base_buffets_url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_org_admin_gets_200(self,api_client,base_buffets_url):
        org = baker.make(Organization)
        org_admin = baker.make(OrganizationAdmin,organization=org)
        api_client.force_authenticate(org_admin.user)
        buffets = baker.make(Buffet,organization=org,_quantity=3)

        response = api_client.get(base_buffets_url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3

    def test_if_client_gets_200(self,api_client,base_buffets_url):
        client = baker.make(Client)
        api_client.force_authenticate(client.user)
        org = baker.make(Organization)
        client.organizations.add(org)
        buffets = baker.make(Buffet,organization=org,_quantity=3)


        response = api_client.get(base_buffets_url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3



    def test_if_no_buffets_get_empty_list(self,api_client,base_buffets_url):
        client = baker.make(Client)
        api_client.force_authenticate(client.user)

        response = api_client.get(base_buffets_url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == []

    def test_if_normal_user_gets_403(self,api_client,base_buffets_url):
        user = baker.make(User)
        api_client.force_authenticate(user)

        response = api_client.get(base_buffets_url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.django_db
class TestBuffetsRetrieve:
    def test_if_anonymous_gets_401(self,api_client,base_buffets_url):
        buffet = baker.make(Buffet)
        response = api_client.get(base_buffets_url+f"{buffet.id}/")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_org_admin_gets_200(self,api_client,base_buffets_url):
        org = baker.make(Organization)
        org_admin = baker.make(OrganizationAdmin,organization=org)
        api_client.force_authenticate(org_admin.user)
        buffet = baker.make(Buffet,organization=org)

        response = api_client.get(base_buffets_url+f"{buffet.id}/")

        assert response.status_code == status.HTTP_200_OK

    def test_if_client_gets_200(self,api_client,base_buffets_url):
        client = baker.make(Client)
        api_client.force_authenticate(client.user)
        org = baker.make(Organization)
        client.organizations.add(org)
        buffet = baker.make(Buffet,organization=org)

        response = api_client.get(base_buffets_url+f"{buffet.id}/")

        assert response.status_code == status.HTTP_200_OK

    def test_if_normal_user_gets_403(self,api_client,base_buffets_url):
        user = baker.make(User)
        api_client.force_authenticate(user)
        buffet = baker.make(Buffet)

        response = api_client.get(base_buffets_url+f"{buffet.id}/")

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestBuffetsCreate:
    def test_if_anonymous_gets_401(self,api_client,base_buffets_url):
        response = api_client.post(base_buffets_url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_org_admin_gets_201(self,api_client,base_buffets_url):
        org = baker.make(Organization)
        org_admin = baker.make(OrganizationAdmin,organization=org)
        api_client.force_authenticate(org_admin.user)
        data = {
            "name":"Buffet 1",
            "organization":org.id
        }

        response = api_client.post(base_buffets_url,data)

        assert response.status_code == status.HTTP_201_CREATED

    def test_if_client_gets_403(self,api_client,base_buffets_url):
        client = baker.make(Client)
        api_client.force_authenticate(client.user)
        org = baker.make(Organization)
        data = {
            "name":"Buffet 1",
            "organization":org.id
        }

        response = api_client.post(base_buffets_url,data)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_normal_user_gets_403(self,api_client,base_buffets_url):
        user = baker.make(User)
        api_client.force_authenticate(user)
        org = baker.make(Organization)
        data = {
            "name":"Buffet 1",
            "organization":org.id
        }

        response = api_client.post(base_buffets_url,data)

        assert response.status_code == status.HTTP_403_FORBIDDEN



@pytest.mark.django_db
class TestBuffetsUpdate:
    def test_if_anonymous_gets_401(self,api_client,base_buffets_url):
        buffet = baker.make(Buffet)
        response = api_client.put(base_buffets_url+f"{buffet.id}/")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_org_admin_gets_200(self,api_client,base_buffets_url):
        org = baker.make(Organization)
        org_admin = baker.make(OrganizationAdmin,organization=org)
        buffet = baker.make(Buffet,organization=org)
        api_client.force_authenticate(org_admin.user)
        data = {
            "name":"Buffet 1",
            "organization":org.id
        }

        response = api_client.put(base_buffets_url+f"{buffet.id}/",data)

        assert response.status_code == status.HTTP_200_OK

    def test_if_client_gets_403(self,api_client,base_buffets_url):
        client = baker.make(Client)
        buffet = baker.make(Buffet)
        api_client.force_authenticate(client.user)
        data = {
            "name":"Buffet 1",
            "organization":buffet.organization.id
        }

        response = api_client.put(base_buffets_url+f"{buffet.id}/",data)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_normal_user_gets_403(self,api_client,base_buffets_url):
        user = baker.make(User)
        buffet = baker.make(Buffet)
        api_client.force_authenticate(user)
        data = {
            "name":"Buffet 1",
            "organization":buffet.organization.id
        }

        response = api_client.put(base_buffets_url+f"{buffet.id}/",data)

        assert response.status_code == status.HTTP_403_FORBIDDEN