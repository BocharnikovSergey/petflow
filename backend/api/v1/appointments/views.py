import logging

from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import viewsets

from .serializers import (
    SlotSerializer, AppointmentReadSerializer, AppointmentWriteSerializer
)
from ..permissions import (
    IsOwnerOrClinicStaff, IsClinicMemberOrAdminOrReadOnly, IsOwner)
from ..mixins import ClinicMixin, ActionReadWriteSerializerMixin
from appointments.models import Appointment


logger = logging.getLogger(__name__)
User = get_user_model()


class SlotViewSet(ClinicMixin, viewsets.ModelViewSet):
    """Управление временными слотами клиники."""

    serializer_class = SlotSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = [IsClinicMemberOrAdminOrReadOnly]

    def get_queryset(self):
        """
        Возвращает все слоты текущей клиники,
        отсортированные по времени начала.
        """
        return self.get_clinic().slots.order_by('start_time')

    def perform_create(self, serializer):
        """Сохраняет слот с привязкой к текущей клинике."""
        serializer.save(clinic=self.get_clinic())


class ClinicAppointmentViewSet(
    ClinicMixin, ActionReadWriteSerializerMixin, viewsets.ModelViewSet
):
    """Управление записями на приём."""

    http_method_names = ['get', 'post', 'patch']
    permission_classes = [IsOwnerOrClinicStaff]
    read_serializer_class = AppointmentReadSerializer
    write_serializer_class = AppointmentWriteSerializer

    def get_queryset(self):
        """
        Возвращает записи,
        доступные пользователю и сотруднику клиники.
        """
        user = self.request.user
        clinic = self.get_clinic()

        return clinic.appointments.filter(
            Q(user=user) | Q(clinic__user_roles__user=user)
        ).distinct().select_related('slot', 'pet', 'user')

    def perform_create(self, serializer):
        """Создаёт запись с текущей клиникой и пользователем."""
        serializer.save(clinic=self.get_clinic(), user=self.request.user)



class MeAppointmentViewSet(
    ActionReadWriteSerializerMixin,
    viewsets.ModelViewSet
):
    """
    Записи текущего пользователя.
    """
    http_method_names = ['get', 'patch']
    permission_classes = [IsOwner]
    read_serializer_class = AppointmentReadSerializer
    write_serializer_class = AppointmentWriteSerializer

    def get_queryset(self):
        return (
            Appointment.objects.filter(user=self.request.user).select_related(
                'clinic', 'slot', 'pet',
            )
        )