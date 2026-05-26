from django.db import models
from django.conf import settings

from core.models import TimeStampedModel
from notifications import constants


class UserNotificationSettings(TimeStampedModel):
    """Моделья настроек уведомлений."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_settings',
        verbose_name='Пользователь.'
    )
    email_enabled = models.BooleanField(
        default=True, verbose_name='Уведомления на почту')
    push_enabled = models.BooleanField(
        default=True, verbose_name='Push-уведомления'
    )


class FCMDevice(TimeStampedModel):
    """Модель для хранения токена для push-уведомлений."""

    class Platform(models.TextChoices):

        IOS = 'ios', 'IOS'
        ANDROID = 'android', 'Android'
        WEB = 'web', 'Web'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='devices'
    )
    token = models.CharField(
        max_length=constants.MAX_LEN_TOKEN,
        unique=True,
        verbose_name='Токен для уведомлений'
    )
    platform = models.CharField(
        max_length=constants.MAX_LEN_PLATFORM,
        choices=Platform.choices,
        verbose_name='Вид платформы для уведомлений'
    )
