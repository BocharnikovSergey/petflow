from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import (
    SpeciesSerializer, BreedReadSerializer, BreedWriteSerializer, 
    PetReadSerializer, PetWriteSerializer, AvatarSerializer,
    MedicalCardSerializer, ChronicConditionSerializer, VaccinationSerializer
)
from ..permissions import (
    IsAdminOrReadOnly, IsPetOwnerOrClinicReadOnly, IsPetOwner,
    IsOwnerOrClinicStaff, IsOwnerReadOrClinicCreatedVisit
)
from ..mixins import ActionReadWriteSerializerMixin, ImageActionMixin
from pets.models import (
    Species, Breed, Pet, MedicalCard, ChronicCondition, Vaccination
)



class SpeciesViewSet(viewsets.ModelViewSet):
    """ViewSet для управления видами животного."""

    queryset = Species.objects.all()
    serializer_class = SpeciesSerializer
    permission_classes = [IsAdminOrReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete']


    @action(detail=True, methods=['get'])
    def breeds(self, request, pk=None):
        """Возвращает список пород для указанного вида животного."""
        species = self.get_object()
        serializer = BreedReadSerializer(
            species.breeds.all().select_related('species'), many=True
        )
        return Response(serializer.data)


class BreedViewSet(ActionReadWriteSerializerMixin, viewsets.ModelViewSet):
    """ViewSet для управления породами животного."""

    queryset = Breed.objects.select_related('species')
    permission_classes = [IsAdminOrReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete']
    read_serializer_class = BreedReadSerializer
    write_serializer_class = BreedWriteSerializer


class PetViewSet(
    ActionReadWriteSerializerMixin, ImageActionMixin, viewsets.ModelViewSet
):

    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = [IsPetOwnerOrClinicReadOnly]
    read_serializer_class = PetReadSerializer
    write_serializer_class = PetWriteSerializer
    image_field = 'avatar'
    serializer_classes = {
        'avatar': AvatarSerializer,
        'medical_card': MedicalCardSerializer,
        'update_medical_card': MedicalCardSerializer,
    }
    

    def get_queryset(self):
        """Возвращает queryset питомцев, доступных текущему пользователю."""
        user = self.request.user
        return Pet.objects.filter(
            Q(owner=user) | Q(appointments__clinic__user_roles__user=user)
        ).distinct().select_related(
            'species', 'breed', 'breed__species', 'owner'
        ).prefetch_related('appointments__clinic__user_roles')

    def perform_create(self, serializer):
        pet = serializer.save()
        MedicalCard.objects.create(pet=pet)
    
    @action(
        detail=True,
        methods=['patch'],
        permission_classes=(IsPetOwner,)
    )
    def avatar(self, request, pk=None):
        """
        Обновление аватара питомца.
        Ожидает multipart/form-data с полем 'avatar'.
        """
        return self._update_image(self.get_object(), request)
    
    @avatar.mapping.delete
    def delete_avatar(self, request, pk=None):
        """
        Удаление аватара питомца. Убирает ссылку на файл и удаляет его с диска.
        """
        return self._delete_image(self.get_object())

    @action(
        detail=True,
        methods=['get'],
        url_path='medical-card',
        permission_classes=(IsPetOwnerOrClinicReadOnly,)
    )
    def medical_card(self, request, pk=None):
        """
        Получение медкарты питомца.
        """
        pet = self.get_object()

        medical_card, _ = MedicalCard.objects.get_or_create(
            pet=pet
        )

        serializer = self.get_serializer(
            medical_card, context={'request': request}
        )
        return Response(serializer.data)
    
    @medical_card.mapping.patch
    def update_medical_card(self, request, pk=None):
        """
        Обновление медкарты питомца.
        """
        pet = self.get_object()
        medical_card, _ = MedicalCard.objects.get_or_create(
            pet=pet
        )
        
        serializer = self.get_serializer(
            medical_card,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


class ChronicConditionViewSet(viewsets.ModelViewSet):
    """
    ViewSet для хронических заболеваний питомца.
    """

    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = [IsOwnerReadOrClinicCreatedVisit]
    serializer_class = ChronicConditionSerializer

    def get_queryset(self):
        """
        Заболевания только конкретного питомца.
        """

        return ChronicCondition.objects.filter(
            medical_card__pet_id=self.kwargs['pet_pk']
        ).select_related(
            'medical_card',
            'medical_card__pet'
        )

    def perform_create(self, serializer):
        """
        Автоматически привязывает заболевание к медкарте питомца.
        """
        pet = get_object_or_404(
            Pet,
            id=self.kwargs['pet_pk']
        )
        serializer.save(
            medical_card=pet.medical_card
        )


class VaccinationViewSet(viewsets.ModelViewSet):
    """
    ViewSet для вакцинаций питомца.
    """

    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = [IsOwnerReadOrClinicCreatedVisit]
    serializer_class = VaccinationSerializer

    def get_queryset(self):
        """
        Вакцинации только конкретного питомца.
        """
        return Vaccination.objects.filter(
            medical_card__pet_id=self.kwargs['pet_pk']
        ).select_related(
            'medical_card',
            'visit',
        )

    def perform_create(self, serializer):
        """
        Автоматически привязывает вакцинацию
        к медкарте питомца.
        """

        pet = get_object_or_404(
            Pet,
            id=self.kwargs['pet_pk']
        )

        serializer.save(
            medical_card=pet.medical_card
        )
