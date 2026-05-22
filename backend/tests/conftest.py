import pytest
from rest_framework.test import APIClient

from tests.factories.users import UserFactory


@pytest.fixture
def api_client():
    """Неавторизованный пользователь"""
    return APIClient()


@pytest.fixture
def user(db):
    """Обычный пользователь."""
    return UserFactory()

@pytest.fixture
def auth_user(api_client, user):
    '''Аутентифицированный пользователь.'''
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def admin(db):
    """Администратор."""
    return UserFactory(role_name='admin')


@pytest.fixture
def auth_admin(api_client, admin):
    '''Аутентифицированный администратор.'''
    api_client.force_authenticate(user=admin)
    return api_client


@pytest.fixture
def user_password():
    return 'qweQWE123!'


@pytest.fixture
def user_email():
    return 'user@user.ru'
