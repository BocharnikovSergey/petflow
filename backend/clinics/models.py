from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator

from core.models import TimeStampedModel
from .utils import constants
from core.utils.constants import MAX_LEN_PHONE
from core.utils.validators import max_size_image


class Address(TimeStampedModel):
    """Модель адреса, который может быть общим для нескольких клиник."""
    city = models.CharField(
        max_length=constants.MAX_LEN_CITY,
        verbose_name='Город'
    )
    street = models.CharField(
        max_length=constants.MAX_LEN_STREET,
        verbose_name='Улица'
    )
    house = models.CharField(
        max_length=constants.MAX_LEN_HOUSE,
        verbose_name='Номер дома'
    )

    class Meta:
        verbose_name = 'Адрес'
        verbose_name_plural = 'Адреса'
        constraints = [
            models.UniqueConstraint(
                fields=['city', 'street', 'house'],
                name='unique_address'
            )
        ]
    
    @property
    def full_address(self):
        return f'г.{self.city}, ул.{self.street}, д.{self.house}'.strip()

    def __str__(self):
        return f'{self.full_address}'
    
    def __repr__(self):
        return (
            f'{self.__class__.__name__}'
            f'(id={self.id}, address={self.full_address})'
        )


class Clinic(TimeStampedModel):
    """Модель ветеринарной клиники."""
    name = models.CharField(
        max_length=constants.MAX_LEN_CLINIC_NAME,
        verbose_name='Название клиники'
    )
    address = models.ForeignKey(
        Address,
        on_delete=models.PROTECT,
        related_name='clinics',
        verbose_name='Адрес'
    )
    phone = models.CharField(
        max_length=MAX_LEN_PHONE,
        blank=True, null=True,
        verbose_name='Телефон'
    )
    email = models.EmailField(
        unique=True,
        verbose_name='Email клиники'
    )
    description = models.TextField(
        blank=True, null=True,
        verbose_name='Описание'
    )
    logo = models.ImageField(
        upload_to='clinics/logos/',
        null=True, blank=True,
        validators=(
            FileExtensionValidator(settings.IMAGE_FORMAT), max_size_image
        ),
        verbose_name='Логотип'
    )

    class Meta:
        verbose_name = 'Клиника'
        verbose_name_plural = 'Клиники'
        ordering = ('name',)

    def __str__(self):
        return self.name
    
    def __repr__(self):
        return (
            f'{self.__class__.__name__}'
            f'(id={self.id}, '
            f'name={self.name}, address={self.address.full_address})'
        )
