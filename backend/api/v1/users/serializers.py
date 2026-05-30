import logging

from django.contrib.auth import get_user_model
from rest_framework import serializers

from users.models import Role, UserRole, VetProfile
from clinics.models import Clinic
from .. import validators
from ..serializers import BaseImageSerializer
from ..pets.serializers import PetShortSerializer
from ..clinics.serializers import ClinicShortSerializer


logger = logging.getLogger(__name__)

User = get_user_model()


class SignUpSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с регистрацией."""

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password']
    
    def validate_email(self, email):
        email = email.strip().lower()
        if User.objects.filter(email=email).exists():
            logger.warning(f'Пользователь с почтой {email} существует')
            raise serializers.ValidationError('Пользователь уже существует')
        return email

    def validate_first_name(self, name):
        return validators.validation_name(name)
    
    def validate_last_name(self, name):
        return validators.validation_name(name)

    def create(self, validated_data):
        """
        Создаёт нового пользователя и автоматически назначает ему роль 'user'
        """
        user = User.objects.create_user(**validated_data, username=None)
        role, _ = Role.objects.get_or_create(name='user')

        UserRole.objects.create(user=user, role=role)
        return user


class SighUpOwnerClinicSerializer(SignUpSerializer):
    """Сериализатор для работы с регистрацией владельца клиник."""

    def create(self, validated_data):
        """
        Создаёт нового пользователя и автоматически назначает ему роль 'owner'
        """
        user = User.objects.create_user(**validated_data, username=None)
        role, _ = Role.objects.get_or_create(name='owner')
        UserRole.objects.create(user=user, role=role)
        return user


class LoginSerializer(serializers.Serializer):
    """Cериализатор для работы с токеном."""

    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        
        user = User.objects.filter(email=email).first()

        if user is None or not user.check_password(password):
            logger.warning(f'Пользователь {email} не может войти.')
            raise serializers.ValidationError('Неверная почта или пароль')
        return data


class TokenResponseSerializer(serializers.Serializer):
    """Сериализатор для вывода токена."""

    access = serializers.CharField()
    refresh = serializers.CharField()
    role = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с пользователем."""

    pets = PetShortSerializer(many=True, read_only=True)
    phone = serializers.CharField(
        required=False, allow_null=True, allow_blank=True,
    )

    class Meta:
        model = User
        fields = (
            'id', 'email', 'phone', 'first_name', 'last_name', 'avatar', 'bio',
            'pets'
        )
        read_only_fields = ('id', 'email', 'avatar')
    
    def validate_first_name(self, name):
        return validators.validation_name(name)
    
    def validate_last_name(self, name):
        return validators.validation_name(name)
    
    def validate_phone(self, phone):
        return validators.validate_phone(phone)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return data


class UserShortSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода краткой информации о пользователе."""

    class Meta:
        model = User
        fields = ('id', 'full_name', 'email', 'phone')


class AvatarSerializer(BaseImageSerializer):
    """Сериализатор для поля аватара пользователя."""

    image_field = 'avatar'

    class Meta:
        model = User
        fields = ('avatar',)


class VetProfileReadSerializer(serializers.ModelSerializer):

    clinic = ClinicShortSerializer(read_only=True)

    class Meta:
        model = VetProfile
        fields = (
            'id', 'clinic', 'email', 'full_name', 'specialization', 'phone',
            'bio',
        )


class VetProfileWriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = VetProfile
        fields = (
            'id', 'email', 'first_name', 'last_name',
            'specialization', 'phone', 'bio', 
        )

    def validate_clinic(self, clinic):
        request = self.context.get('request')
        user = request.user

        if not Clinic.objects.filter(
            owner=user,
        ).exists():
            raise serializers.ValidationError(
                """Клиника не пренадлежит пользователю."""
            )
        return clinic

    def validate_first_name(self, name):
        return validators.validation_name(name)
    
    def validate_last_name(self, name):
        return validators.validation_name(name)
    
    def validate_phone(self, phone):
        return validators.validate_phone(phone)
    
    def validate_specialization(self, specialization):
        return validators.validation_name(specialization)

    def to_representation(self, instance):
        return VetProfileReadSerializer(instance, context=self.context).data


class AvatarVetSerializer(BaseImageSerializer):
    """Сериализатор для поля аватара ветеринара."""

    image_field = 'avatar'

    class Meta:
        model = VetProfile
        fields = ('avatar',)
