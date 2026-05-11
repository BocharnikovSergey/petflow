from django.contrib.auth import get_user_model
from rest_framework import serializers

from users.models import Role, UserRole
from ..utils import validations
from ..serializers import BaseImageSerializer
from ..pets.serializers import PetShortSerializer


User = get_user_model()


class SignUpSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации."""

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password']
    
    def validate_email(self, email):
        email = email.strip().lower()
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError('Пользователь уже существует')
        return email

    def validate_first_name(self, first_name):
        return validations.validation_name(first_name)

    def validate_last_name(self, last_name):
        return validations.validation_name(last_name)


    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password'],
            username=None,
        )
        role, _ = Role.objects.get_or_create(name='user')

        UserRole.objects.create(
            user=user,
            role=role,
        )
        return user


class LoginSerializer(serializers.Serializer):
    """Cериализатор для токена."""

    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        
        user = User.objects.filter(email=email).first()

        if user is None or not user.check_password(password):
            raise serializers.ValidationError('Неверная почта или пароль')
        return data


class TokenResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):

    pets = PetShortSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'email', 'first_name', 'last_name', 'avatar', 'bio', 'pets'
        )
        read_only_fields = ('id', 'email', 'avatar')

    def validate_first_name(self, first_name):
        return validations.validation_name(first_name)

    def validate_last_name(self, last_name):
        return validations.validation_name(last_name)


class AvatarSerializer(BaseImageSerializer):

    image_field = 'avatar'

    class Meta:
        model = User
        fields = ('avatar',)
