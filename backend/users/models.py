from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.db import models

from .utils import constants
from core.utils.validators import max_size_image


class ProjectUser(AbstractUser):
    """Кастомная модель пользователя."""

    email = models.EmailField(
        unique=True,
        verbose_name='Адрес электронной почты',
    )
    first_name = models.CharField(
        max_length=constants.MAX_LEN_NAME, verbose_name='Имя',
    )
    last_name = models.CharField(
        max_length=constants.MAX_LEN_NAME, verbose_name='Фамилия',
    )
    avatar = models.ImageField(
        upload_to=constants.UPLOAD_TO_USERS,
        blank=True, null=True,
        verbose_name='Аватар',
        validators=(
            FileExtensionValidator(settings.IMAGE_FORMAT), max_size_image
        ),
    )
    phone = models.CharField(
        max_length=constants.MAX_LEN_PHONE,
        blank=True, null=True, verbose_name='Телефон'
    )
    bio = models.TextField(blank=True, null=True, verbose_name='О себе')
    username = models.CharField(
        max_length=constants.MAX_LEN_USERNAME, blank=True, null=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username','first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('email',)

    def __str__(self):
        return f'{self.first_name}, {self.last_name}'strip()
    
    def __repr__(self):
        return (
            f'{self.__class__.__name__}'
            f'(id={self.id}, '
            f'first_name={self.first_name}, last_name={self.last_name})'
        )

class Role(models.Model):
    """Роль пользователя."""
    name = models.CharField(
        max_length=constants.MAX_LEN_ROLE_NAME,
        verbose_name='Название роли'
    )

    class Meta:
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'
        ordering = ('name',)

    def __str__(self):
        return self.name
    
    def __repr__(self):
        return f'{self.__class__.__name__}(id={self.id}, name={self.name})'


class UserRole(models.Model):
    """Связь между пользователем и ролью."""
    user = models.ForeignKey(
        ProjectUser,
        on_delete=models.CASCADE,
        related_name='roles',
        verbose_name='Пользователь'
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='users',
        verbose_name='Роль'
    )
    clinic = models.ForeignKey(
        'Clinic',
        on_delete=models.CASCADE,
        blank=True, null=True,
        related_name='user_roles',
        verbose_name='Клиника'
    )

    class Meta:
        verbose_name = 'Роль пользователя'
        verbose_name_plural = 'Роли пользователей'
        ordering = ('user',)