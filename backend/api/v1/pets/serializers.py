from rest_framework import serializers

from api.v1 import constants
from pets.models import Species, Breed, Pet
from ..serializers import BaseImageSerializer


class SpeciesSerializer(serializers.ModelSerializer):
    """Сериализатор для вида животного."""
    name = serializers.CharField(min_length=constants.MIN_LEN_NAME)

    class Meta:
        model = Species
        fields = ('id', 'name')


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
    name = serializers.CharField(min_length=constants.MIN_LEN_NAME)


    class Meta:
        model = Breed
        fields = ('id', 'name', 'species')


class PetReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения питомца."""

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

    class Meta:
        model = Pet
        fields = ('id', 'name', 'species')


class PetWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для создания питомца."""

    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    species = serializers.PrimaryKeyRelatedField(
        queryset=Species.objects.all()
    )
    breed = serializers.PrimaryKeyRelatedField(
        queryset=Breed.objects.all(),
        required=False,
        allow_null=True
    )
    name = serializers.CharField(min_length=constants.MIN_LEN_NAME)

    class Meta:
        model = Pet
        fields = (
            'id', 'owner', 'name', 'species', 'breed', 'birth_date', 'weight',
        )
    
    def validate(self, attrs):
        species = attrs.get('species')
        breed = attrs.get('breed')

        if breed and species and breed.species != species:
            raise serializers.ValidationError({
                'breed': 'Порода не соответствует виду животного'
            })

        return attrs


class PetShortSerializer(serializers.ModelSerializer):

    class Meta:
        model = Pet
        fields = ('id', 'name', 'avatar')


class AvatarSerializer(BaseImageSerializer):

    image_field = 'avatar'

    class Meta:
        model = Pet
        fields = ('avatar',)

