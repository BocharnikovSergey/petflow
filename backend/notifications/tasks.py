from datetime import datetime

from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

from appointments.models import Appointment
from notifications.constants import REMINDER_BEFORE_APPOINTMENT
from .services import send_fcm_multicast, deactivate_invalid_tokens


def get_appointment_for_notification(appointment_id):
    return Appointment.objects.select_related(
        'clinic', 'slot', 'user', 'user__notification_settings'
    ).get(id=appointment_id)


@shared_task
def send_user_email_appointment(
    appointment_id, subject, notification_type='created'
):
    """Таска для отправки сообщения пользователю по email."""
    appointment = get_appointment_for_notification(
        appointment_id=appointment_id
    )
    appointment_datetime = timezone.make_aware(datetime.combine(
        appointment.date, appointment.slot.start_time
        ))
    if (
        appointment.user.notification_settings.email_enabled
        and (
            notification_type in {'created', 'canceled'}
            or (
                notification_type=='reminder'
                and appointment.status != Appointment.AppointmentStatus.CANCELED
                and timezone.now() < appointment_datetime - REMINDER_BEFORE_APPOINTMENT
            )
        )
    ):
        send_mail(
            subject=subject,
            message=(
                f'Вы записаны в клинику {appointment.clinic.name} '
                f'по адресу {appointment.clinic.address} '
                f'на {appointment.date} в {appointment.slot.start_time}'
            ),
            from_email=settings.EMAIL_ADMIN,
            recipient_list=['bocharnikov_sergey@mail.ru'],
            fail_silently=False,
        )


@shared_task
def send_user_push_appointment(appointment_id):
    """Таска для отправки push-уведомления пользователю напоминание о записи."""

    appointment = get_appointment_for_notification(appointment_id)
    appointment_datetime = timezone.make_aware(datetime.combine(
        appointment.date, appointment.slot.start_time
        ))
    if (
        appointment.user.notification_settings.push_enabled
        and appointment.status != Appointment.AppointmentStatus.CANCELED
        and appointment_datetime - REMINDER_BEFORE_APPOINTMENT
    ):
        devices = appointment.user.devices.filter(is_active=True)
        tokens = [device.token for device in devices]

        response = send_fcm_multicast(
            tokens=tokens,
            title='Напоминание о записи',
            body=(
                f'У вас запись в клинику {appointment.clinic.name} '
                f'{appointment.date.strftime("%d.%m.%Y")} в '
                f'{appointment.slot.start_time.strftime("%H:%M")}'
            )
        )
        if response:
            deactivate_invalid_tokens(tokens=tokens, response=response)


@shared_task
def send_clinic_email_appointment(appointment_id, subject):
    """Таска для отправки сообщения клиники о записи на почту."""
    appointment = Appointment.objects.select_related(
        'clinic__owner__notification_settings', 'user', 'pet', 'slot',
        'pet__species'
    ).get(id=appointment_id)

    if appointment.clinic.owner.notification_settings.email_enabled:
        send_mail(
            subject=subject,
            message=(
                f'В клинику {appointment.clinic.name} записан '
                f'{appointment.user.full_name} '
                f'c питомцем {appointment.pet.name}({appointment.pet.species}) '
                f'на {appointment.date} в {appointment.slot.start_time}'
            ),
            from_email=settings.EMAIL_ADMIN,
            recipient_list=[
                'bocharnikov_sergey@mail.ru', appointment.user.email
            ],
            fail_silently=False,
        )


@shared_task
def send_clinic_push_appointment(appointment_id):
    """Пуш уведомление владельцу клиники о новой записи."""

    appointment = Appointment.objects.select_related(
        'clinic__owner', 'clinic__owner__notification_settings', 'user', 'slot'
    ).get(id=appointment_id)

    if appointment.clinic.owner.notification_settings.push_enabled:

        devices = appointment.clinic.owner.devices.filter(is_active=True)
        tokens = [device.token for device in devices]

        response = send_fcm_multicast(
            tokens=tokens,
            title='Новая запись в клинику',
            body=(
                f'В клинику {appointment.clinic.name} '
                f'записан клиент {appointment.user.full_name}. '
                f'Дата: {appointment.date.strftime("%d.%m.%Y")} '
                f'{appointment.slot.start_time.strftime("%H:%M")}'
            )
        )
        if response:
            deactivate_invalid_tokens(tokens, response)


def send_appointment_notifications(
    appointment, subject='Запись в клинику', notification_type='created'
):
    """Отправляет уведомления пользователю и клинике о создании записи."""

    send_user_email_appointment.delay(
        appointment.id, subject, notification_type
    )
    # send_clinic_email_appointment.delay(appointment.id, subject)
    # send_clinic_push_appointment.delay(appointment.id, notification_type)


def schedule_appointment_reminder(appointment):
    """Создаёт отложенное уведомление для пользователя."""

    eta_time = timezone.make_aware(datetime.combine(
            appointment.date, appointment.slot.start_time
        ) - REMINDER_BEFORE_APPOINTMENT)

    send_user_email_appointment.apply_async(
        args=[appointment.id],
        kwargs={
            'subject': 'Напоминание о бронирование',
            'notification_type': 'reminder'
        },
        eta=eta_time,
    )
    send_user_push_appointment.apply_async(args=[appointment.id], eta=eta_time,)
