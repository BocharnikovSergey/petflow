import pytest
from rest_framework import status

from tests import constants
from users.models import ProjectUser


@pytest.mark.django_db
def test_user_registration(api_client, user_password, user_email):
    """Проверяет успешную регистрацию пользователя."""
    response = api_client.post(
        constants.URL_SIGHUP,
        data={
            'email': user_email,
            'password': user_password,
            'first_name': 'Test',
            'last_name': 'User',
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    users = ProjectUser.objects.filter(email=user_email)

    assert set(response.data.keys()) == {'email', 'first_name', 'last_name'}
    assert response.data['email'] == user_email

    assert users.count() == 1
    user = users.first()
    assert user.first_name == 'Test'
    assert user.check_password(user_password) is True
    assert user.roles.filter(role__name='user').exists()


@pytest.mark.django_db
@pytest.mark.parametrize(
    'email',
    [
        '',
        'invalid-email',
        'user@',
        '@user.ru',
    ],
)
def test_user_registration_invalid_email(api_client, email):
    """Проверяет невалидную почту."""
    response = api_client.post(
        constants.URL_SIGHUP,
        data={
            'email': email,
            'password': 'qweQWE123!',
            'first_name': 'Test',
            'last_name': 'User',
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'email' in response.data


@pytest.mark.django_db
@pytest.mark.parametrize(
    'password',
    ['', '123', 'qweqweqwe', 'qwe', 'qweQWEqwe', 'qweQWE123'],
)
def test_user_registration_invalid_password(api_client, password):
    """Проверяет не валидные пароли."""
    response = api_client.post(
        constants.URL_SIGHUP,
        data={
            'email': 'user@test.com',
            'password': password,
            'first_name': 'Test',
            'last_name': 'User',
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'password' in response.data


@pytest.mark.django_db
def test_login_returns_jwt_tokens(api_client, user):
    """Проверяет что при входе возвращает токены."""
    response = api_client.post(
        constants.URL_LOGIN,
        data={
            'email': user.email,
            'password': 'qweQWE123!',
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert 'access' in response.data
    assert 'refresh' in response.data
    assert isinstance(response.data['access'], str)
    assert isinstance(response.data['refresh'], str)


@pytest.mark.django_db
def test_access_token_auth(api_client, user):
    """Токен доступа позволяет получить доступ к защищенному пути."""

    response = api_client.post(
        constants.URL_LOGIN,
        data={
            'email': user.email,
            'password': 'qweQWE123!',
        }
    )
    access_token = response.data['access']
    api_client.credentials(
        HTTP_AUTHORIZATION=f'Bearer {access_token}'
    )
    response = api_client.get(constants.URL_USERS_ME)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_access_without_token_fails(api_client):
    """
    Защищенный путь должен отклонять запрос от пользователя без аутентификации.
    """
    response = api_client.get(constants.URL_USERS_ME)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_invalid_token_fails(api_client):
    """Недействительный токен должен быть отклонен."""

    api_client.credentials(
        HTTP_AUTHORIZATION='Bearer invalid_token'
    )
    response = api_client.get(constants.URL_USERS_ME)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
