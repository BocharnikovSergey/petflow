from django.db.models import Avg

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly, IsAuthenticated
)
from rest_framework.response import Response

from clinics.models import Address, Clinic
from .serializers import (
    AddressSerializer, ClinicReadSerializer, ClinicWriteSerializer,
    LogoSerializer
)


class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all().order_by('city', 'street')
    # permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = AddressSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']


class ClinicViewSet(viewsets.ModelViewSet):

    queryset = Clinic.objects.select_related('address').annotate(
            rating=Avg('reviews__score')
        )
    http_method_names = ['get', 'post', 'patch', 'delete']


    def get_serializer_class(self):
        if self.action in {'create', 'update', 'partial_update'}:
            return ClinicWriteSerializer
        elif self.action == 'logo':
            return LogoSerializer
        return ClinicReadSerializer


    # убрать дублирование в питомцах и пользователе
    @action(
        detail=True,
        methods=['patch'],
        permission_classes=(IsAuthenticated,)
    )
    def logo(self, request, pk=None):
        clinic = self.get_object()
        serializer = self.get_serializer(clinic, data=request.data,  partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @logo.mapping.delete
    def delete_logo(self, request, pk=None):
        clinic = self.get_object()
        if not clinic.logo:
            return Response(
                {'detail': 'Нет лого.'}, status.HTTP_400_BAD_REQUEST
            )

        clinic.logo.delete(save=False)
        clinic.logo = None
        clinic.save(update_fields=['logo'])
        return Response(
            {'detail': 'Лого успешно удалено.'},
            status=status.HTTP_204_NO_CONTENT
        )

