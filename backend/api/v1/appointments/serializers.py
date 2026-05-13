from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from appointments.models import Appointment, Slot
from ..users.serializers import UserShortSerializer
from ..clinics.serializers import ClinicShortSerializer
from ..pets.serializers import PetShortSerializer


User = get_user_model()


class SlotSerializer(serializers.ModelSerializer):

    clinic = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Slot
        fields = ('id', 'clinic', 'start_time', 'end_time')
    
    def validate(self, attrs):
        start_time = attrs.get(
            'start_time',
            getattr(self.instance, 'start_time', None)
        )
        end_time = attrs.get(
            'end_time',
            getattr(self.instance, 'end_time', None)
        )

        if end_time <= start_time:
            raise serializers.ValidationError({
                'end_time': (
                    'Время окончания должно быть позже времени начала.'
                )
            })

        if Slot.objects.filter(
            clinic=self.context['view'].get_clinic(),
            start_time__lt=end_time, end_time__gt=start_time,
        ).exclude(pk=getattr(self.instance, 'pk', None)).exists():
            raise serializers.ValidationError(
                'Этот временной слот пересекается с существующим.'
            )
        return attrs

class SlotShortSerializer(serializers.ModelSerializer):

    class Meta:
        model = Slot
        fields = ('start_time', 'end_time')


class AppointmentReadSerializer(serializers.ModelSerializer):

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

    class Meta:
        model = Appointment
        fields = (
            'id',
            'pet',
            'date',
            'slot',
            'comment',
        )

    def validate_pet(self, pet):
        request = self.context['request']
        if pet.owner != request.user:
            raise serializers.ValidationError(
                'Нельзя записать чужого питомца.'
            )
        return pet
    
    def validate_date(seld, date):
        if timezone.now().date() < date:
            raise serializers.ValidationError(
                'Дата не может быть в прошлом.'
            )
        return date

    def validate_slot(self, slot):
        clinic = self.context['view'].kwargs['clinic_id']
        if slot.clinic.id != int(clinic):
            raise serializers.ValidationError(
                'Слот не принадлежит выбранной клинике.'
        )
        return slot

    def validate(self, attrs):
        """Проверка записи."""

        if Appointment.objects.filter(
            clinic=self.context['view'].kwargs['clinic_id'],
            slot=attrs.get('slot'),
            date=attrs.get('date')
        ).exists():
            raise serializers.ValidationError({
                'slot': 'Этот слот уже занят.'
            })
        return attrs
