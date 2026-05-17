import re

from rest_framework import serializers
from PIL import Image

from . import constants
from .utils.services import normalize_address


def validation_name(value):
    """Валидирует имя или фамилию пользователя."""
       
    if not isinstance(value, str):
        raise serializers.ValidationError(constants.ERROR_INVALID_NAME)
        
    value = value.strip()
    if not value or len(value) < constants.MIN_LEN_NAME:
        raise serializers.ValidationError(constants.ERROR_INVALID_NAME)

    return value.strip().title()


def validation_image(file):
    if file:
        if file.size > constants.MAX_SIZE_IMAGE_MB * 1024 * 1024:
            raise serializers.ValidationError(
                f'Файл не должен превышать {constants.MAX_SIZE_IMAGE_MB}MB'
            )
        try:
            img = Image.open(file)
            img.verify()
        except Exception:
            raise serializers.ValidationError('Файл не является изображением')
        
        file.seek(0)
        with Image.open(file) as img:
            if img.format.lower() not in constants.IMAGE_FORMAT:
                raise serializers.ValidationError(
                    f'Разрешен формат: {", ".join(constants.IMAGE_FORMAT)}'
                )
    return file


def validate_field_address(value, pattern):
    """Универсальная валидация поля адресса."""
    if not isinstance(value, str):
        raise serializers.ValidationError('Неверный тип данных в поле')
    value = value.strip()
    if not re.fullmatch(pattern=pattern, string=value):
        raise serializers.ValidationError(
            f'Содержит недопустимые символы.'
        )
    return normalize_address(value)

def validate_city_and_street(value):
    """Валидация названия городов и улиц."""
    return validate_field_address(
        value, pattern=constants.PATTERN_CITY_OR_STREET
    )


def validate_house(value):
    """Валидация дома."""
    return validate_field_address(
        value, pattern=constants.PATTERN_HOUSE)


def validate_phone(value):
    """Валидация телефона."""

    if not value:
        return value
    
    digits = re.sub(r'[^\d+]', '', value)

    if not digits.startswith('+'):
        digits = '+' + digits

    if not re.fullmatch(r'\+\d{7,15}', digits):
        raise serializers.ValidationError(
            'Введите корректный номер телефона.'
        )

    return digits
