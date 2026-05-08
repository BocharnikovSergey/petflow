from djoser import serializers
from django.contrib.auth import get_user_model

from users.utils import constants

User = get_user_model()

# Добавить сериализатор для аватара.

class SignUpSerializer(serializers.UserCreateSerializer):
    """Сериализатор для регистрации."""

    class Meta(serializers.UserCreateSerializer.Meta):
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'password')


class ProjectUserSerializer(serializers.UserSerializer):
    """Сериализатор для профиля пользователя."""

    class Meta(UserSerializer.Meta):
        model = User
        fields = (
            'id', 'email', 'first_name', 'last_name', 'avatar', 'phone', 'bio'
        )
