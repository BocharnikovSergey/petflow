from rest_framework import serializers

from clinics.models import Clinic, Address
from .. import validators
from ..serializers import BaseImageSerializer


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
        if Address.objects.filter(
            city=attrs['city'],
            street=attrs['street'],
            house=attrs['house']
        ).exists():
            raise serializers.ValidationError(
                'Такой адрес уже существует.'
            )
        return attrs


class ClinicReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения клиники."""

    address = AddressSerializer(read_only=True)

    class Meta:
        model = Clinic
        fields = (
            'id', 'name', 'address', 'phone', 'email', 'description', 'logo'
        )


class ClinicWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для создания клиники."""

    address = serializers.PrimaryKeyRelatedField(
        queryset=Address.objects.all()
    )

    phone = serializers.CharField(
        required=False, allow_null=True, allow_blank=True,
        validators=[validators.validate_phone]
    )

    class Meta:
        model = Clinic
        fields = (
            'id', 'name', 'address', 'phone', 'email', 'description'
        )


class LogoSerializer(BaseImageSerializer):

    image_field = 'logo'

    class Meta:
        model = Clinic
        fields = ('logo',)

