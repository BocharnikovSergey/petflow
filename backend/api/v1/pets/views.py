from django.db.models import Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import (
    SpeciesSerializer, BreedReadSerializer, BreedWriteSerializer, 
    PetReadSerializer, PetWriteSerializer, AvatarSerializer
)
from ..permissions import (
    IsAdminOrReadOnly, IsPetOwnerOrClinicReadOnly, IsPetOwner
)
from ..mixins import ActionReadWriteSerializerMixin, ImageActionMixin
from pets.models import Species, Breed, Pet



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
    serializer_classes = {'avatar': AvatarSerializer}
    

    def get_queryset(self):
        """Возвращает queryset питомцев, доступных текущему пользователю."""
        user = self.request.user
        return Pet.objects.filter(
            Q(owner=user) | Q(appointments__clinic__user_roles__user=user)
        ).distinct().select_related(
            'species', 'breed', 'breed__species', 'owner'
        ).prefetch_related('appointments__clinic__user_roles')

    
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
