
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from .serializers import (
    SlotSerializer, AppointmentReadSerializer, AppointmentWriteSerializer
)
from clinics.models import Clinic


User = get_user_model()


class SlotViewSet(viewsets.ModelViewSet):

    serializer_class = SlotSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_clinic(self):
        """Получает произведение по id из URL."""
        if not hasattr(self, '_clinic'):
            self._clinic = get_object_or_404(
                Clinic, id=self.kwargs.get('clinic_id')
            )
        return self._clinic

    def get_queryset(self):
        return self.get_clinic().slots.order_by('start_time')

    def perform_create(self, serializer):
        serializer.save(clinic=self.get_clinic())


class AppointmentViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in {'create', 'update', 'partial_update'}:
            return AppointmentWriteSerializer
        return AppointmentReadSerializer

    def get_clinic(self):
        """Получает произведение по id из URL."""
        if not hasattr(self, '_clinic'):
            self._clinic = get_object_or_404(
                Clinic, id=self.kwargs.get('clinic_id')
            )
        return self._clinic

    def get_queryset(self):
        return self.get_clinic().appointments.filter(
            user=self.request.user
        ).select_related('slot', 'pet', 'user')

    def perform_create(self, serializer):
        serializer.save(clinic=self.get_clinic(), user=self.request.user)

