from rest_framework import serializers

from api.v1 import constants
from pets.models import Species, Breed, Pet
from ..serializers import BaseImageSerializer
from ..validators import validation_name


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

    def to_representation(self, instance):
        return PetReadSerializer(instance, context=self.context).data

    def validate_name(self, name):
        return validation_name(name)


class AvatarSerializer(BaseImageSerializer):

    image_field = 'avatar'

    class Meta:
        model = Pet
        fields = ('avatar',)

