import logging

from rest_framework import serializers

from pets.models import Species, Breed, Pet
from ..serializers import BaseImageSerializer
from ..validators import validation_name


logger = logging.getLogger(__name__)


class SpeciesSerializer(serializers.ModelSerializer):
    """Сериализатор для вида животного."""

    class Meta:
        model = Species
        fields = ('id', 'name')
    
    def validate_name(self, name):
        return validation_name(name)


class BreedReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения породы животного."""

    species = SpeciesSerializer()

    class Meta:
        model = Breed
        fields = ('id', 'name', 'species')


class BreedReadSimpleSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода породы животного в питомце."""

    class Meta:
        model = Breed
        fields = ('id', 'name')


class BreedWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для создания породы животного."""

    species = serializers.PrimaryKeyRelatedField(
        queryset=Species.objects.all()
    )

    class Meta:
        model = Breed
        fields = ('id', 'name', 'species')
    
    def validate_name(self, name):
        return validation_name(name)



class PetReadSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода информации питомца."""

    species = SpeciesSerializer()
    breed = BreedReadSimpleSerializer()
    owner = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Pet
        fields = (
            'id', 'owner', 'name', 'species', 'breed', 'birth_date', 'weight',
            'avatar'
        )


class PetShortSerializer(serializers.ModelSerializer):
    """Краткая информация о питомце."""

    class Meta:
        model = Pet
        fields = ('id', 'name', 'species')


class PetWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для создания,обновления питомца."""

    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    species = serializers.PrimaryKeyRelatedField(
        queryset=Species.objects.all()
    )
    breed = serializers.PrimaryKeyRelatedField(
        queryset=Breed.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Pet
        fields = (
            'id', 'owner', 'name', 'species', 'breed', 'birth_date', 'weight',
        )
    
    def validate(self, attrs):
        """ Проверяет соответствие породы указанному виду животного."""
        species = attrs.get('species')
        breed = attrs.get('breed')

        if breed and species and breed.species != species:
            logger.warning(
                f'Порода {breed} не соответсвует виду животного {species}'
            )
            raise serializers.ValidationError({
                'breed': 'Порода не соответствует виду животного'
            })

        return attrs

    def to_representation(self, instance):
        return PetReadSerializer(instance, context=self.context).data

    def validate_name(self, name):
        return validation_name(name)


class AvatarSerializer(BaseImageSerializer):
    """Сериализатор для поля аватара питомца."""

    image_field = 'avatar'

    class Meta:
        model = Pet
        fields = ('avatar',)
