import pytest
from user.models import User
from rest_framework.test import APIClient
from django.urls import reverse
from pytest_factoryboy import register
from user.models import Role
from user.tests.factories import (
    UserFactory, TokenFactory,PermissionFactory, RoleFactory
)

register(UserFactory)
register(TokenFactory)
register(PermissionFactory)


@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def active_user(db, user_factory):
    return user_factory.create(is_active=True)

@pytest.fixture
def inactive_user(db, user_factory):
    user = user_factory.create(is_active=False)
    return user

@pytest.fixture
def auth_user_password()->str:
    '''returns user password to be used in authentication'''
    return 'passer@@@111'

@pytest.fixture
def authenticate_user(api_client, active_user: User,auth_user_password):
    """Create a user, assign specified role and returns token needed for authentication"""
    def _user(verified=True, is_active = True,is_admin=False, role="", permissions = []):
        active_user.verified = verified
        active_user.is_active = is_active
        active_user.is_admin = is_admin
        active_user.save()
        if permissions:
            created_role = RoleFactory(permissions=permissions)
            active_user.roles.add(created_role)
        active_user.refresh_from_db()
        url = reverse("auth:login")
        data = {
           "email": active_user.email,
           "password": auth_user_password,
        }
        response = api_client.post(url, data)
        token = response.json()["access"]
        return {
             "token": token,
             "user_email": active_user.email,
             "user_instance": active_user,
        }
         
    return _user


@pytest.fixture
def seed_roles():
    """Seed specified roles into the db"""
    def _roles(role_names =[]):
        user_roles = [Role(name = each) for each in role_names ]
        return Role.objects.bulk_create(user_roles)     
    return _roles