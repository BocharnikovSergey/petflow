from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .serializers import (
    SpeciesSerializer, BreedReadSerializer, BreedWriteSerializer, 
    PetReadSerializer, PetWriteSerializer, AvatarSerializer
)
from ..permissions import (
    IsAdminOrReadOnly, IsPetOwnerOrClinicReadOnly, IsPetOwner
)
from pets.models import Species, Breed, Pet



class SpeciesViewSet(viewsets.ModelViewSet):
    """Вью для вида животного."""

    queryset = Species.objects.all()
    serializer_class = SpeciesSerializer
    permission_classes = [IsAdminOrReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete']


    @action(detail=True, methods=['get'])
    def breeds(self, request, pk=None):
        species = self.get_object()
        serializer = BreedReadSerializer(
            species.breeds.all().select_related('species'), many=True
        )
        return Response(serializer.data)


class BreedViewSet(viewsets.ModelViewSet):
    """Вью для породы животного."""

    queryset = Breed.objects.select_related('species')
    permission_classes = [IsAdminOrReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete']


    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return BreedWriteSerializer
        return BreedReadSerializer


class PetViewSet(viewsets.ModelViewSet):

    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = [IsPetOwnerOrClinicReadOnly]

    def get_queryset(self):
        user = self.request.user
        return Pet.objects.filter(
            Q(owner=user) | Q(appointments__clinic__user_roles__user=user)
        ).distinct().select_related(
            'species', 'breed', 'breed__species', 'owner'
        ).prefetch_related('appointments__clinic__user_roles')


    def get_serializer_class(self):
        if self.action in ['create', 'update']:
            return PetWriteSerializer
        elif self.action == 'avatar':
            return AvatarSerializer
        return PetReadSerializer
    
    @action(
        detail=True,
        methods=['patch'],
        permission_classes=(IsPetOwner,)
    )
    def avatar(self, request, pk=None):
        pet = self.get_object()
        serializer = self.get_serializer(pet, data=request.data,  partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @avatar.mapping.delete
    def delete_avatar(self, request, pk=None):
        pet = self.get_object()
        if not pet.avatar:
            return Response(
                {'detail': 'Нет аватара.'}, status.HTTP_400_BAD_REQUEST
            )

        pet.avatar.delete(save=False)
        pet.avatar = None
        pet.save(update_fields=['avatar'])
        return Response(
            {'detail': 'Аватар успешно удален.'},
            status=status.HTTP_204_NO_CONTENT
        )

    
