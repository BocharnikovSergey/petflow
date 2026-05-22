import pytest
from rest_framework import status

from tests import constants


@pytest.mark.django_db
def test_admin_role(admin):
    """Проверяет роль администратора."""

    assert admin.has_any_role('admin') is False

@pytest.mark.django_db
@pytest.mark.parametrize(
    'client_fixture',
    ['auth_admin', 'auth_user', 'api_client']
)
def test_addresses_permissions(request, client_fixture):
    """Проверяет, что список адресов доступен всем пользователям."""
    client = request.getfixturevalue(client_fixture)
    response = client.get(constants.ADDRESSES_URL)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    'client_fixture, expected_status',
    [
        ('auth_admin', status.HTTP_201_CREATED),
        ('auth_user', status.HTTP_403_FORBIDDEN),
        ('api_client', status.HTTP_401_UNAUTHORIZED),
    ]
)
def test_create_address_permissions(request, client_fixture, expected_status):
    """
    Проверяет доступ на создание адреса в зависимости от роли пользователя.
    """
    client = request.getfixturevalue(client_fixture)
    response = client.post(
        constants.ADDRESSES_URL,
        data={
            'city': 'Москва',
            'street': 'Ленина',
            'house': '50'
        }
    )

    assert response.status_code == expected_status