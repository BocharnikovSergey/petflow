from django.db import models
from django.contrib.auth import get_user_model

from .utils import constants
from core.utils.validators import max_size_image
from core.models import TimeStampedModel

User = get_user_model()


class Species(TimeStampedModel):
    """Модель для вида животного."""

    name = models.CharField(
        max_length=constants.MAX_LEN_SPECIES,
        unique=True,
        verbose_name='Название вида'
    )

    class Meta:
        verbose_name = 'Вид животного'
        verbose_name_plural = 'Виды животных'
        ordering = ('name',)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'{self.__class__.__name__}(id={self.id}, name={self.name})'


class Breed(TimeStampedModel):
    """Порода животного, привязанная к виду."""
    species = models.ForeignKey(
        Species,
        on_delete=models.CASCADE,
        related_name='breeds',
        verbose_name='Вид животного'
    )
    name = models.CharField(
        max_length=constants.MAX_LEN_BREED,
        verbose_name='Название породы'
    )

    class Meta:
        verbose_name = 'Порода'
        verbose_name_plural = 'Породы'
        ordering = ('species', 'name')
        constraints = [
            models.UniqueConstraint(
                fields=['species', 'name'], 
                name='unique_breed_per_species'
            )
        ]

    def __str__(self):
        return f'{self.name} ({self.species.name})'
    
    def __repr__(self):
        return (
            f'{self.__class__.__name__}'
            f'(id={self.id}, name={self.name}, species={self.species.name}'
        )

class Pet(TimeStampedModel):
    """Модель питомца."""
    
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='pets',
        verbose_name='Владелец'
    )
    name = models.CharField(
        max_length=constants.MAX_LEN_PET_NAME,
        verbose_name='Кличка'
    )
    species = models.ForeignKey(
        'Species',
        on_delete=models.PROTECT,
        related_name='pets',
        verbose_name='Вид'
    )
    breed = models.ForeignKey(
        'Breed',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='pets',
        verbose_name='Порода'
    )
    birth_date = models.DateField(
        blank=True, null=True,
        verbose_name='Дата рождения'
    )
    weight = models.DecimalField(
        max_digits=constants.WEIGHT_MAX_DIGITS,
        decimal_places=constants.WEIGHT_DECIMAL_PLACES,
        blank=True, null=True,
        verbose_name='Вес (кг)'
    )
    avatar = models.ImageField(
        upload_to='pets/avatars/',
        blank=True, null=True,
        verbose_name='Фото питомца'
        validators=(
            FileExtensionValidator(settings.IMAGE_FORMAT), max_size_image
        ),
    )

    class Meta:
        verbose_name = 'Питомец'
        verbose_name_plural = 'Питомцы'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name} ({self.owner.email})'
