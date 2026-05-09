from django.db import models


class TimeStampedModel(models.Model):
    """Абстрактный набор полей для контроля жизненного цикла записи."""

    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    class Meta:
        abstract = True
