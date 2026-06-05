import uuid
import os

from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.http import FileResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response

from clinics.models import Address, Clinic, Visit
from pets.models import Pet
from .serializers import (
    AddressSerializer, ClinicReadSerializer, ClinicWriteSerializer,
    LogoSerializer, VisitReadSerializer, VisitWriteSerializer,
    VisitAttachmentSerializer
)
from .filters import ClinicFilter
from ..permissions import (
    IsAdminOrReadOnly, IsClinicStaffOrAdminOrReadOnly, IsOwnerReadOrClinicCreatedVisit
)
from ..mixins import ActionReadWriteSerializerMixin, ImageActionMixin
from ..utils.services import get_coordinates
import logging

logger = logging.getLogger(__name__)


class AddressViewSet(viewsets.ModelViewSet):
    """ViewSet для управления адресами."""

    queryset = Address.objects.all().order_by('city', 'street')
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = AddressSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']


class ClinicViewSet(
    ActionReadWriteSerializerMixin, ImageActionMixin, viewsets.ModelViewSet
):
    """ViewSet для управления клиниками."""

    queryset = Clinic.objects.select_related('address').annotate(
            rating=Avg('reviews__score')
        )
    permission_classes = [IsClinicStaffOrAdminOrReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )
    filterset_class = ClinicFilter
    search_fields = ('name', 'address__city', 'address__street')
    ordering_fields = ('name', 'rating',)
    read_serializer_class = ClinicReadSerializer
    write_serializer_class = ClinicWriteSerializer
    image_field = 'logo'
    serializer_classes = {'logo': LogoSerializer}

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsClinicStaffOrAdminOrReadOnly,)
    )
    def my(self, request, pk=None):
        """Получение всех клиник владельца."""
        queryset = self.get_queryset().filter(owner=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        

    @action(
        detail=True,
        methods=['patch'],
        permission_classes=(IsClinicStaffOrAdminOrReadOnly,)
    )
    def logo(self, request, pk=None):
        """
        Обновление логотипа клиники.
        Ожидает multipart/form-data с полем 'logo'.
        """
        return self._update_image(self.get_object(), request)

    @logo.mapping.delete
    def delete_logo(self, request, pk=None):
        """
        Удаление логотипа клиники. Убирает ссылку на файл и удаляет его с диска.
        """
        return self._delete_image(self.get_object())
    
    


class VisitViewSet(ActionReadWriteSerializerMixin,viewsets.ModelViewSet):

    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = [IsOwnerReadOrClinicCreatedVisit]
    read_serializer_class = VisitReadSerializer
    write_serializer_class = VisitWriteSerializer

    def get_queryset(self):
        pet_id = self.kwargs.get('pet_pk')
        user = self.request.user
        queryset = Visit.objects.select_related('clinic', 'pet',).filter(
            pet_id=pet_id
        )
        if hasattr(user, 'pets') and user.pets.filter(id=pet_id).exists():
            return queryset
        if hasattr(user, 'clinics') and user.clinics.exists():
            return queryset.filter(clinic__in=user.clinics.all())
        return queryset.none()
    
    def perform_create(self, serializer):
        pet = get_object_or_404(
            Pet,
            id=self.kwargs['pet_pk']
        )

        serializer.save(
            pet=pet,
        )
    
    @action(
        detail=True, 
        methods=['post'], 
        url_path='upload-attachment',
        serializer_class=VisitAttachmentSerializer,
        permission_classes=(IsOwnerReadOrClinicCreatedVisit,)
    )
    def upload_attachment(self, request, pet_pk=None, pk=None):
        """
        Загрузка файла для конкретного визита.
        """
        visit = self.get_object()
        serializer = self.get_serializer(
            visit,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data['attachments']

        file_extension = os.path.splitext(file.name)[1]
        new_filename = f'visit_{visit.id}_{uuid.uuid4().hex}{file_extension}'
        
        visit.attachments.save(new_filename, file, save=True)
        read_serializer = self.read_serializer_class(
            visit, context={'request': request}
        )
        return Response(read_serializer.data, status=status.HTTP_200_OK)
    
    @action(
        detail=True,
        methods=['get'],
        url_path='download-attachment',
        permission_classes=(IsOwnerReadOrClinicCreatedVisit,)
    )
    def download_attachment(self, request, pet_pk=None, pk=None):
        """
        Скачать файл визита.
        """
        visit = self.get_object()
        if not visit.attachments:
            return Response(
                {'detail': 'Файл не найден.'},
                status=status.HTTP_404_NOT_FOUND
            )

        return FileResponse(
            visit.attachments.open('rb'),
            as_attachment=True,
            filename=os.path.basename(
                visit.attachments.name
            )
        )
            


