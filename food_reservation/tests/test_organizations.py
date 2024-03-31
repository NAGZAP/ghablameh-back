from django.conf import settings
from rest_framework import status
from food_reservation.models import Organization,OrganizationAdmin
from django.contrib.auth import get_user_model,authenticate
from model_bakery import baker
from rest_framework.test import APIClient
import pytest

User = get_user_model()



@pytest.fixture
def base_organizations_url():
    return f"/api/v{settings.VERSION}/organizations/"


@pytest.mark.django_db
class TestChangePasswordMyOrganization:
    
    
    def test_if_old_password_not_valid_return_400(self,api_client,base_organizations_url):
        org_admin = baker.make(OrganizationAdmin,user__username='a',user__password='a')
        org       = baker.make(Organization,admin=org_admin)
        user = org.admin.user
        user.set_password('a')
        user.save()
        api_client.force_authenticate(user=org.admin.user)
        data = {
            "old_password": 'b',
            "new_password": "admin_1234"
        } 
        
        response = api_client.post(base_organizations_url+"password/",data=data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not user.check_password(data["new_password"])
    
    def test_if_new_password_not_valid_return_400(self,api_client,base_organizations_url):
        org_admin = baker.make(OrganizationAdmin,user__username='a',user__password='a')
        org       = baker.make(Organization,admin=org_admin)
        user = org.admin.user
        user.set_password('a')
        user.save()
        api_client.force_authenticate(user=org.admin.user)
        data = {
            "old_password": 'a',
            "new_password": "b"
        } 
        
        response = api_client.post(base_organizations_url+"password/",data=data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not user.check_password(data["new_password"])
        
    
    def test_if_all_ok(self,api_client,base_organizations_url):
        org_admin = baker.make(OrganizationAdmin,user__username='a',user__password='a')
        org       = baker.make(Organization,admin=org_admin)
        user = org.admin.user
        user.set_password('a')
        user.save()
        api_client.force_authenticate(user=org.admin.user)
        data = {
            "old_password": 'a',
            "new_password": "admin_1234"
        } 
        
        response = api_client.post(base_organizations_url+"password/",data=data)
        
        assert response.status_code == status.HTTP_200_OK
        assert user.check_password(data["new_password"])
        
    def test_if_user_is_normal_user_returns_403(self,api_client,base_organizations_url):
        org_admin = baker.make(OrganizationAdmin,user__username='a',user__password='a')
        org       = baker.make(Organization,admin=org_admin)
        user = org.admin.user
        user.set_password('a')
        user.save()
        api_client.force_authenticate(user=User())
        data = {
            "old_password": 'a',
            "new_password": "admin_1234"
        } 
        
        response = api_client.post(base_organizations_url+"password/",data=data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert not user.check_password(data["new_password"])
    
    
    
    def test_if_user_is_anonymous_returns_401(self,api_client,base_organizations_url):
        org_admin = baker.make(OrganizationAdmin,user__username='a',user__password='a')
        org       = baker.make(Organization,admin=org_admin)
        user = org.admin.user
        user.set_password('a')
        user.save()
        data = {
            "old_password": 'a',
            "new_password": "admin_1234"
        } 
        
        response = api_client.post(base_organizations_url+"password/",data=data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert not user.check_password(data["new_password"])
        
    



@pytest.mark.django_db
class TestUpdateMyOrganization:
    
    def test_org_name_was_taken(self,api_client,base_organizations_url):
        org_admin = baker.make(OrganizationAdmin,user__username='a',user__password='a')
        org       = baker.make(Organization,admin=org_admin)
        api_client.force_authenticate(user=org.admin.user)
        duplicated_org = baker.make(Organization,name='a')
        data = {
            "name": 'a',
            "admin_username": "b"
        } 
        
        response = api_client.put(base_organizations_url+"me/",data=data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        
    def test_username_was_taken(self,api_client,base_organizations_url):
        org_admin = baker.make(OrganizationAdmin,user__username='a',user__password='a')
        org       = baker.make(Organization,admin=org_admin)
        api_client.force_authenticate(user=org.admin.user)
        duplicated_user = baker.make(User,username='b')
        data = {
            "name": 'a',
            "admin_username": "b"
        } 
        
        response = api_client.put(base_organizations_url+"me/",data=data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    
    def test_if_all_ok(self,api_client,base_organizations_url):
        org_admin = baker.make(OrganizationAdmin,user__username='a',user__password='a')
        org       = baker.make(Organization,admin=org_admin)
        api_client.force_authenticate(user=org.admin.user)
        data = {
            "name": 'a',
            "admin_username": "b"
        } 
        
        response = api_client.put(base_organizations_url+"me/",data=data)
        
        assert response.status_code == status.HTTP_200_OK
        
    def test_if_user_is_normal_user_returns_403(self,api_client,base_organizations_url):
        org_admin = baker.make(OrganizationAdmin,user__username='a',user__password='a')
        org       = baker.make(Organization,admin=org_admin)
        api_client.force_authenticate(user=User())
        data = {
            "name": 'a',
            "admin_username": "b"
        } 
        
        response = api_client.put(base_organizations_url+"me/",data=data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    
    
    def test_if_user_is_anonymous_returns_401(self,api_client,base_organizations_url):
        org_admin = baker.make(OrganizationAdmin,user__username='a',user__password='a')
        org       = baker.make(Organization,admin=org_admin)
        data = {
            "name": 'a',
            "admin_username": "b"
        } 
        
        response = api_client.put(base_organizations_url+"me/",data=data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        
    



@pytest.mark.django_db
class TestGetMyOrganization:
    
    def test_if_user_is_normal_user_returns_403(self,api_client,base_organizations_url):
        org_admin = baker.make(OrganizationAdmin,user__username='a',user__password='a')
        org       = baker.make(Organization,admin=org_admin)
        api_client.force_authenticate(user=User())
        
        response = api_client.get(base_organizations_url+"me/")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    
    
    def test_if_user_is_anonymous_returns_401(self,api_client,base_organizations_url):
        org_admin = baker.make(OrganizationAdmin,user__username='a',user__password='a')
        org       = baker.make(Organization,admin=org_admin)
        
        response = api_client.get(base_organizations_url+"me/")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    
    def test_if_all_ok(self,api_client,base_organizations_url):
        org_admin = baker.make(OrganizationAdmin,user__username='a',user__password='a')
        org       = baker.make(Organization,admin=org_admin)
        api_client.force_authenticate(user=org.admin.user)
        
        response = api_client.get(base_organizations_url+"me/")
        
        assert response.status_code == status.HTTP_200_OK
        



@pytest.mark.django_db
class TestLoginOrganization:
    
    def test_if_all_ok(self,api_client,base_organizations_url):
        org_admin = baker.make(OrganizationAdmin,user__username='a',user__password='a')
        org       = baker.make(Organization,admin=org_admin)
        user = org.admin.user
        user.set_password('a')
        user.save()
        data = {
            'username':'a',
            'password':'a'
        }
        
        response = api_client.post(base_organizations_url+'login/',data=data)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'tokens' in response.data
        
        
    def test_if_username_or_password_is_incorrect(self,api_client,base_organizations_url):
        org_admin = baker.make(OrganizationAdmin,user__username='a',user__password='a')
        org       = baker.make(Organization,admin=org_admin)
        user = org.admin.user
        user.set_password('a')
        user.save()
        data = {
            'username':'b',
            'password':'a'
        }

        response = api_client.post(base_organizations_url+'login/',data=data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'tokens' not in response.data
        
        data = {
            'username':'a',
            'password':'b'
        }
        
        response = api_client.post(base_organizations_url+'login/',data=data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'tokens' not in response.data
    


@pytest.mark.django_db
class TestRegisterOrganization:
    
    
    def test_if_all_ok(self,api_client,base_organizations_url):
        data = {
            "organization_name" : "a",
            "username": "a",
            "password": "test_pass_1234",
            "email": "user@example.com",
            "first_name": "a",
            "last_name": "b",
            "phone_number": "+989123456789"
        }
        
        response = api_client.post(base_organizations_url+"register/",data=data)
        user_queryset = User.objects.filter(
            username=data["username"],
            first_name = data["first_name"],
            last_name = data["last_name"],
            email = data["email"],
            phone_number = data["phone_number"])
        
        
        assert response.status_code == status.HTTP_201_CREATED
        assert OrganizationAdmin.objects.filter(organization__name = data["organization_name"])
        assert Organization.objects.filter(name=data["organization_name"]).exists()
        assert user_queryset.exists()
        assert user_queryset.get().check_password(data['password'])
        
        
        
    def test_if_organization_name_taken(self,api_client,base_organizations_url):
        baker.make(Organization,name='a')
        data = {
            "organization_name" : "a",
            "username": "a",
            "password": "test_pass_1234",
            "email": "user@example.com",
            "first_name": "a",
            "last_name": "b",
            "phone_number": "+989123456789"
        }
        
        response = api_client.post(base_organizations_url+"register/",data=data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not User.objects.filter(username=data["username"]).exists()
        assert not OrganizationAdmin.objects.filter(organization__name = data["organization_name"])
        
        
        
        
    def test_if_username_taken(self,api_client,base_organizations_url):
        baker.make(User,username='a')
        data = {
            "organization_name" : "a",
            "username": "a",
            "password": "test_pass_1234",
            "email": "user@example.com",
            "first_name": "a",
            "last_name": "b",
            "phone_number": "+989123456789"
        }
        
        response = api_client.post(base_organizations_url+"register/",data=data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not Organization.objects.filter(name=data["organization_name"]).exists()
        assert not OrganizationAdmin.objects.filter(organization__name = data["organization_name"])
        
        
    def test_if_phone_number_taken(self,api_client,base_organizations_url):
        baker.make(User,phone_number="+989123456789")
        data = {
            "organization_name" : "a",
            "username": "a",
            "password": "test_pass_1234",
            "email": "user@example.com",
            "first_name": "a",
            "last_name": "b",
            "phone_number": "+989123456789"
        }
        
        response = api_client.post(base_organizations_url+"register/",data=data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not Organization.objects.filter(name=data["organization_name"]).exists()
        assert not OrganizationAdmin.objects.filter(organization__name = data["organization_name"])
        
        
    
    def test_if_email_taken(self,api_client,base_organizations_url):
        baker.make(User,email="user@example.com")
        data = {
            "organization_name" : "a",
            "username": "a",
            "password": "test_pass_1234",
            "email": "user@example.com",
            "first_name": "a",
            "last_name": "b",
            "phone_number": "+989123456789"
        }
        
        response = api_client.post(base_organizations_url+"register/",data=data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not Organization.objects.filter(name=data["organization_name"]).exists()
        assert not OrganizationAdmin.objects.filter(organization__name = data["organization_name"])
                
        

@pytest.mark.django_db
class TestListOrganization:
    
    def test_if_no_organization_have(self,api_client,base_organizations_url):
        response = api_client.get(base_organizations_url)
        
        assert response.status_code == status.HTTP_200_OK 
        assert len(response.data) == 0


    def test_if_all_ok(self,api_client,base_organizations_url):
        orgs = baker.make(Organization,_quantity=3)
        
        
        response = api_client.get(base_organizations_url)
        response_orgs:list = response.data

        assert response.status_code == status.HTTP_200_OK
        assert len(response_orgs) == len(orgs)
        assert list(map(lambda org:org['name'],response_orgs)) == list(map(lambda org:org.name,orgs)) 