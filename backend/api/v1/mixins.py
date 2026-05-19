from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from clinics.models import Clinic


class ClinicMixin:
    """
    Миксин для вьюсетов, которые работают с клиникой,
    переданной в параметре URL `clinic_id`.
    """
    def get_clinic(self):
        if not hasattr(self, '_clinic'):
            clinic_id = self.kwargs.get('clinic_id')
            self._clinic = get_object_or_404(Clinic, id=clinic_id)
        return self._clinic


class ClinicAccessMixin:
    """
    Миксин, предоставляющий метод is_clinic_allowed
    для проверки доступа пользователя к клинике.
    """

    def is_clinic_allowed(self, user, clinic):
        """Проверяет, имеет ли пользователь доступ к клинике."""
        return (
            user.is_superuser
            or user.has_any_role('admin')
            or user.is_clinic_member(clinic)
        )   


class ActionReadWriteSerializerMixin:
    """
    Автоматически использует write_serializer для create/update/partial_update,
    read_serializer для остальных действий.
    Можно переопределить конкретные actions через serializer_classes.
    """
    read_serializer_class = None
    write_serializer_class = None
    serializer_classes = {}

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return self.write_serializer_class
        return self.serializer_classes.get(
            self.action, self.read_serializer_class or super().get_serializer_class()
        )

class ImageActionMixin:
    """Миксин с общей логикой для работы с изображением."""
    image_field = None

    def _update_image(self, obj, request):
        """Обновление изображения у переданного объекта."""
        serializer = self.get_serializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def _delete_image(self, obj):
        """Удаление изображения у переданного объекта."""
        field_value = getattr(obj, self.image_field)
        if not field_value:
            return Response(
                {'detail': f'Нет {self.image_field}.'},
                status=status.HTTP_400_BAD_REQUEST
                )
        field_value.delete(save=False)
        setattr(obj, self.image_field, None)
        obj.save(update_fields=[self.image_field])
        return Response(
            {'detail': f'{self.image_field} удалён.'},
            status=status.HTTP_204_NO_CONTENT
        )
