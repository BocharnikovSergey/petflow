from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets,filters
from rest_framework.decorators import action

from clinics.models import Address, Clinic
from .serializers import (
    AddressSerializer, ClinicReadSerializer, ClinicWriteSerializer,
    LogoSerializer
)
from .filters import ClinicFilter
from ..permissions import IsAdminOrReadOnly, IsClinicStaffOrAdminOrReadOnly
from ..mixins import ActionReadWriteSerializerMixin, ImageActionMixin


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

