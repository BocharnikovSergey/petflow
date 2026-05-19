from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

from core.models import TimeStampedModel
from clinics.models import Clinic
from .utils import constants


class Review(TimeStampedModel):
    """Модель отзыва о клинике."""
    
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор отзыва'
    )
    clinic = models.ForeignKey(
        Clinic,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Клиника'
    )
    text = models.TextField(
        verbose_name='Текст отзыва'
    )
    score = models.PositiveSmallIntegerField(
        verbose_name='Оценка',
        validators=[
            MinValueValidator(
                constants.MIN_SCORE, 
                message=f'Минимальная оценка - {constants.MIN_SCORE}'
            ),
            MaxValueValidator(
                constants.MAX_SCORE,
                message=f'Максимальная оценка - {constants.MAX_SCORE}'
            )
        ],
        help_text=(
            f'Выберите оценку от {constants.MIN_SCORE} до {constants.MAX_SCORE}'
        )
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ('clinic',)
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'clinic'],
                name='unique_review_per_user'
            )
        ]

    def __str__(self):
        return f'Отзыв от {self.author.full_name} на {self.clinic.name}'
    
    def __repr__(self):
        return (
            f'{self.__class__.__name__} '
            f'(id={self.id}, '
            f'author={self.author.full_name}, clinic={self.clinic.name})'
        )
    
