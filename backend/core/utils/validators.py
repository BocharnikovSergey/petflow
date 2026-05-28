from django.conf import settings
from django.core.exceptions import ValidationError
from rest_framework import serializers

from .constants import (
    MAX_SIZE_IMAGE_MB, MAX_SIZE_FILE_MB, FILE_FORMAT, IMAGE_FORMAT
)


def max_size_image(image):
    """Валидатор максимального размера изображения."""
    if image.size > MAX_SIZE_IMAGE_MB * 1024 * 1024:
        raise ValidationError(
            'Максимальный размер изображения не должен превышать'
            f'{MAX_SIZE_IMAGE_MB} МБ.'
        )


def max_size_file(file):
    """Валидатор максимального размера файла."""
    if file.size > MAX_SIZE_FILE_MB * 1024 * 1024:
        raise ValidationError(
            'Максимальный размер файла не должен превышать'
            f'{MAX_SIZE_IMAGE_MB} МБ.'
        )


def image_format(format):
    if format.lower() not in IMAGE_FORMAT:
        raise serializers.ValidationError(
            f'Формат изображения "{format}" не поддерживается.'
            f'{", ".join(IMAGE_FORMAT)}'
        )


def file_format(format):
    if format.lower() not in settings.IMAGE_FORMAT:
        raise serializers.ValidationError(
            f'Формат файла "{format}" не поддерживается.'
            f'{", ".join(FILE_FORMAT)}'
        )
