import logging

from django.utils import timezone
from rest_framework import serializers

from pets.models import (
    Species, Breed, Pet, ChronicCondition, Vaccination, MedicalCard
)
from clinics.models import Visit
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


class ChronicConditionSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра хронических заболеваний."""

    class Meta:
        model = ChronicCondition
        fields = ('id', 'name', 'description', 'status')
    
    def validate_name(self, name):
        return validation_name(name)



class VaccinationSerializer(serializers.ModelSerializer):
    """Сериализатор вакцинации."""

    class Meta:
        model = Vaccination
        fields = (
            'id', 'visit', 'name', 'vaccinated_at', 'expires_at', 'notes',
        )
    
    def validate_name(self, name):
        return validation_name(name)
    
    def validate_vaccinated_at(self, vaccinated_at):
        if vaccinated_at > timezone.now().date():
            raise serializers.ValidationError(
                'Дата вакцинации не может быть в будущем.'
            )

        return vaccinated_at

    def validate(self, attrs):
        vaccinated_at = attrs.get(
            'vaccinated_at',
            self.instance.vaccinated_at if self.instance else None
        )
        expires_at = attrs.get(
            'expires_at',
            self.instance.expires_at if self.instance else None
        )
        if (
            expires_at
            and vaccinated_at
            and expires_at < vaccinated_at
        ):
            raise serializers.ValidationError({
                'expires_at': (
                    'Срок действия не может быть раньше даты вакцинации.'
                )
            })
        visit = attrs.get(
            'visit',
            self.instance.visit if self.instance else None
        )
        if visit:
            pet_id = self.context['view'].kwargs.get('pet_pk')
            if visit.pet_id != int(pet_id):
                raise serializers.ValidationError({
                    'visit': 'Визит не принадлежит питомцу.'
                })
        return attrs


class MedicalCardSerializer(serializers.ModelSerializer):
    """
    Детальная медкарта питомца.
    """

    conditions = ChronicConditionSerializer(
        many=True,
        read_only=True
    )

    vaccinations = VaccinationSerializer(
        many=True,
        read_only=True
    )

    visits = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = MedicalCard

        fields = (
            'id', 'notes', 'allergies', 'conditions', 'vaccinations', 'visits',
        )

    def get_visits(self, obj):
        from ..clinics.serializers import VisitReadSerializer

        visits = Visit.objects.filter(
            pet=obj.pet
        ).select_related(
            'clinic'
        )

        return VisitReadSerializer(
            visits,
            many=True,
            context=self.context
        ).data
