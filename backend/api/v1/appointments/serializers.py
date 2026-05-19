import logging

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from appointments.models import Appointment, Slot
from ..users.serializers import UserShortSerializer
from ..clinics.serializers import ClinicShortSerializer
from ..pets.serializers import PetShortSerializer


logger = logging.getLogger(__name__)
User = get_user_model()


class SlotSerializer(serializers.ModelSerializer):
    """Сериализатор для создания/обновления слотов."""

    clinic = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Slot
        fields = ('id', 'clinic', 'start_time', 'end_time')
    
    def validate(self, attrs):
        """
        Проверяет,
        что время окончания позже начала и слот не пересекается с существующими.
        """
        start_time = attrs.get(
            'start_time',
            getattr(self.instance, 'start_time', None)
        )
        end_time = attrs.get(
            'end_time',
            getattr(self.instance, 'end_time', None)
        )

        if end_time <= start_time:
            message = (
                'Время окончания должно быть позже времени начала'
                f'{end_time} <= {start_time}'
            )
            logger.warning(message)
            raise serializers.ValidationError({'end_time': message})

        if Slot.objects.filter(
            clinic=self.context['view'].get_clinic(),
            start_time__lt=end_time, end_time__gt=start_time,
        ).exclude(pk=getattr(self.instance, 'pk', None)).exists():
            message = (
                f'Временной слот {start_time}-{end_time} '
                'пересекается с существующим.'
            )
            logger.warning(message)
            raise serializers.ValidationError(message)
        return attrs


class SlotShortSerializer(serializers.ModelSerializer):
    """Краткая информация о слоте (только время)."""

    class Meta:
        model = Slot
        fields = ('start_time', 'end_time')


class AppointmentReadSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода информации приема."""

    clinic = ClinicShortSerializer(read_only=True)
    slot = SlotShortSerializer(read_only=True)
    pet = PetShortSerializer(read_only=True)
    user = UserShortSerializer(read_only=True)

    class Meta:
        model = Appointment
        fields = (
            'id', 'pet', 'date', 'clinic', 'slot', 'comment', 'user', 'status',
        )


class AppointmentWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для записи (создания/обновления) приема."""

    class Meta:
        model = Appointment
        fields = ('id', 'pet', 'date', 'slot', 'comment')

    def validate_pet(self, pet):
        request = self.context['request']
        if pet.owner != request.user:
            message = 'Нельзя записать чужого питомца.'
            logger.error(message)
            raise serializers.ValidationError(message)
        return pet
    
    def validate_date(self, date):
        if timezone.now().date() > date:
            message = f'Дата {date} не может быть в прошлом.'
            logger.warning(message)
            raise serializers.ValidationError(message)
        return date

    def validate_slot(self, slot):
        clinic = self.context['view'].kwargs['clinic_id']
        if slot.clinic.id != int(clinic):
            message = 'Слот не принадлежит клинике.'
            logger.warning(message)
            raise serializers.ValidationError(message)
        return slot

    def validate(self, attrs):
        """Проверяет, что дата/время не в прошлом и слот свободен."""

        date = attrs.get('date')
        slot = attrs.get('slot')

        time_now = timezone.now()

        if date == time_now.date() and slot.start_time <= time_now.time():
            message = 'Нельзя записаться на прошедшее время.'
            logger.warning(message)
            raise serializers.ValidationError({'slot': message})

        if Appointment.objects.filter(
            clinic=self.context['view'].kwargs['clinic_id'],
            slot=attrs.get('slot'),
            date=attrs.get('date')
        ).exists():
            message = 'Слот уже занят.'
            logger.warning(message)
            raise serializers.ValidationError({'slot': message})
        return attrs

    def to_representation(self, instance):
        return AppointmentReadSerializer(instance, context=self.context).data
