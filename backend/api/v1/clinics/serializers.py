import logging

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from clinics.models import Clinic, Address
from .. import validators
from ..serializers import BaseImageSerializer


logger = logging.getLogger(__name__)


class AddressSerializer(serializers.ModelSerializer):
    """Сериализатор для адресов."""

    city = serializers.CharField(
        validators=[validators.validate_city_and_street]
    )
    street = serializers.CharField(
        validators=[validators.validate_city_and_street]
    )
    house = serializers.CharField(
        validators=[validators.validate_house]
    )
    full_address = serializers.ReadOnlyField()
    
    class Meta:
        model = Address
        fields = ('id', 'city', 'street', 'house', 'full_address')
    
    def validate(self, attrs):
        """
        Проверяет,
        что адрес с указанными городом, улицей и домом ещё не существует в БД.
        """
        city = attrs.get('city')
        street = attrs.get('street')
        house = attrs.get('house')
        if Address.objects.filter(city=city,street=street,house=house).exists():
            logger.warning(
                'Попытка создать дублирующийся адрес: '
                f'{city}, {street}, {house}'
            )
            raise serializers.ValidationError('Такой адрес уже существует.')
        return attrs


class ClinicReadSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода информации о клинике."""

    address = AddressSerializer(read_only=True)
    rating = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Clinic
        fields = (
            'id', 'name', 'address', 'phone', 'email', 'description', 'logo',
            'rating'
        )

    @extend_schema_field(serializers.FloatField())
    def get_rating(self, obj):
        """
        Возвращает рейтинг объекта.
        Если рейтинг отсутствует, возвращает 0.
        """
        return round(getattr(obj, 'rating', 0) or 0, 1)


class ClinicShortSerializer(serializers.ModelSerializer):
    """Краткая информация о клинике"""

    class Meta:
        model = Clinic
        fields = ('id', 'name', 'address', 'phone', 'email')


class ClinicWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для создания/обновления клиники."""

    address = serializers.PrimaryKeyRelatedField(
        queryset=Address.objects.all()
    )

    phone = serializers.CharField(
        required=False, allow_null=True, allow_blank=True,
    )

    class Meta:
        model = Clinic
        fields = (
            'id', 'name', 'address', 'phone', 'email', 'description'
        )
    
    def to_representation(self, instance):
        return ClinicReadSerializer(instance, context=self.context).data
    
    def validate_phone(self, phone):
        return validators.validate_phone(phone)


class LogoSerializer(BaseImageSerializer):
    """Сериализатор для поля логотипа клиники."""

    image_field = 'logo'

    class Meta:
        model = Clinic
        fields = ('logo',)
