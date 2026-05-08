from django.conf import settings
from django.core.exceptions import ValidationError
from rest_framework import serializers


def max_size_image(image):
    """Валидатор максимального размера изображения."""
    if image.size > settings.MAX_SIZE_IMAGE_MB * 1024 * 1024:
        raise ValidationError(
            'Максимальный размер изображения не должен превышать'
            f'{settings.MAX_SIZE_IMAGE_MB} МБ.'
        )


def image_format(format):
    if format.lower() not in settings.IMAGE_FORMAT:
        raise serializers.ValidationError(
            f'Формат изображения "{format}" не поддерживается.'
            f'{", ".join(settings.IMAGE_FORMAT)}'
        )
