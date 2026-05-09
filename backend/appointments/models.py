from django.db import models
from django.contrib.auth import get_user_model

from core.models import TimeStampedModel
from .utils import constants
from pets.models import Pet
from clinics.models import Clinic


User = get_user_model()


class AppointmentStatus(models.TextChoices):
    """Статусы записи."""

    PENDING = ('pending', 'Ожидает подтверждения')
    CONFIRMED = ('confirmed', 'Подтверждено')
    CANCELED = ('canceled', 'Отменено')
    COMPLETED = ('completed', 'Завершено')


class Slot(TimeStampedModel):
    """Доступные временные слоты для записи в клинику."""
    clinic = models.ForeignKey(
        Clinic,
        on_delete=models.CASCADE,
        related_name='slots',
        verbose_name='Клиника'
    )
    start_time = models.TimeField(verbose_name='Дата и время начала')
    end_time = models.TimeField(verbose_name='Дата и время окончания')

    class Meta:
        verbose_name = 'Доступное время'
        verbose_name_plural = 'Доступное время'
        ordering = ('start_time',)
        constraints = [
            models.UniqueConstraint(
                fields=['clinic', 'start_time'],
                name='unique_slot_per_clinic'
            )
        ]
    def __str__(self):
        return f'{self.clinic.name}: {self.start_time} - {self.end_time}'

    def __repr__(self):
        return (
            f'{self.__class__.__name__} '
            f'(clinic={self.clinic.name}, '
            f'slot={self.start_time} - {self.end_time})'
        )


class Appointment(TimeStampedModel):
    """Модель записи пользователя с питомцем в клинику."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name='Пользователь'
    )
    pet = models.ForeignKey(
        Pet,
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name='Питомец'
    )
    date = models.DateField(
        verbose_name='Дата записи'
    )
    clinic = models.ForeignKey(
        Clinic,
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name='Клиника'
    )
    slot = models.ForeignKey(
        Slot,
        on_delete=models.PROTECT,
        related_name='appointment',
        verbose_name='Временной слот'
    )
    status = models.CharField(
        max_length=constants.MAX_LEN_STATUS,
        choices=AppointmentStatus.choices,
        default=AppointmentStatus.PENDING,
        verbose_name='Статус записи'
    )
    comment = models.TextField(
        blank=True, null=True,
        verbose_name='Комментарий пользователя'
    )

    class Meta:
        verbose_name = 'Запись на прием'
        verbose_name_plural = 'Записи на прием'
        ordering = ('date', 'slot__start_time')
        constraints = [
            models.UniqueConstraint(
                fields=['slot', 'date', 'clinic'], 
                name='unique_appointment_slot'
            )
        ]

    def __str__(self):
        return (
            f'{self.user.full_name}-{self.pet.name}'
            f'({self.date}:{self.slot.start_time})'
        )
    
    def __repr__(self):
        return (
            f'{self.__class__.__name__} '
            f'(user={self.user.full_name}, '
            f'pet={self.pet.name}, '
            f'date={self.date}, '
            f'clinic={self.clinic.name}, '
            f'slot={self.slot.start_time}-{self.slot.end_time}, '
            f'status={self.status})'
        )