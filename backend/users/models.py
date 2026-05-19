import logging

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import FileExtensionValidator
from django.db import models

from .utils import constants
from core.utils.constants import MAX_LEN_PHONE, IMAGE_FORMAT
from core.utils.validators import max_size_image
from clinics.models import Clinic


logger = logging.getLogger(__name__)


class ProjectUserManager(BaseUserManager):
    """Кастомный менеджер для пользователя."""

    def create_user(self, email, password=None, **extra_fields):
        """Создание обычного пользователя."""
        if not email:
            logger.warning('Email обязвтелное поле.')
            raise ValueError('Email обязателен')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Создание суперпользователя."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        return self.create_user(email, password, **extra_fields)


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
            FileExtensionValidator(IMAGE_FORMAT), max_size_image
        ),
    )
    phone = models.CharField(
        max_length=MAX_LEN_PHONE,
        blank=True, null=True, verbose_name='Телефон'
    )
    bio = models.TextField(blank=True, null=True, verbose_name='О себе')
    username = models.CharField(
        max_length=constants.MAX_LEN_USERNAME, blank=True, null=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = ProjectUserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('email',)

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()

    def __str__(self):
        return self.full_name

    def __repr__(self):
        return (
            f'{self.__class__.__name__}'
            f'(id={self.id}, '
            f'first_name={self.first_name}, last_name={self.last_name})'
        )
    
    def has_any_role(self, *role_names):
        """
        Проверяет, имеет ли пользователь хотя бы одну из переданных ролей.
        """
        return self.roles.filter(role__name__in=role_names).exists()
    
    def is_clinic_member(self, clinic):
        """Проверяет, является ли пользователь членом указанной клиники."""
        return self.roles.filter(clinic=clinic).exists()


class Role(models.Model):
    """Роль пользователя."""

    name = models.CharField(
        max_length=constants.MAX_LEN_ROLE_NAME,
        verbose_name='Название роли'
    )
    description = models.TextField(
        blank=True, null=True, verbose_name='Описание роли.'
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
        Clinic,
        on_delete=models.CASCADE,
        blank=True, null=True,
        related_name='user_roles',
        verbose_name='Клиника'
    )
    description = models.TextField(
        blank=True, null=True, verbose_name='Описание.'
    )

    class Meta:
        verbose_name = 'Роль пользователя'
        verbose_name_plural = 'Роли пользователей'
        ordering = ('user',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'role', 'clinic'],
                name='unique_user_role_clinic'
            )
        ]
