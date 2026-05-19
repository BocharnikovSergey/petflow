import re
import logging

from rest_framework import serializers
from PIL import Image, UnidentifiedImageError

from . import constants
from .utils.services import normalize_address


logger = logging.getLogger(__name__)


def validation_name(value):
    """Валидирует название поля."""
    if (
        not isinstance(value, str)
        or not (value := value.strip())
        or len(value) < constants.MIN_LEN_NAME
    ):
        message = 'Не корректное значение'
        logger.warning(message + f'{value}')
        raise serializers.ValidationError(message)
    return value.title()


def validation_image(file):
    """Проверяет, что переданный файл является корректным изображением."""
    if file:
        if file.size > constants.MAX_SIZE_IMAGE_MB * 1024 * 1024:
            raise serializers.ValidationError(
                f'Файл не должен превышать {constants.MAX_SIZE_IMAGE_MB}MB'
            )
        try:
            img = Image.open(file)
            img.verify()
        except UnidentifiedImageError:
            message = 'Файл не является изображением (неопознанный формат)'
            logger.warning(message)
            raise serializers.ValidationError(message)
        except (IOError, OSError) as error:
            message = f'Ошибка чтения изображения: {str(error)}'
            logger.error(message)
            raise serializers.ValidationError(message)
        except Exception as error:
            logger.exception(
                f'Неожиданная ошибка при проверке изображения {error}'
            )
            raise serializers.ValidationError('Некорректный файл изображения')
        
        file.seek(0)
        with Image.open(file) as img:
            if img.format.lower() not in constants.IMAGE_FORMAT:
                logger.warning(f'Неверный формат изображения {img.format}')
                raise serializers.ValidationError(
                    f'Разрешен формат: {", ".join(constants.IMAGE_FORMAT)}'
                )
    return file


def validate_field_address(value, pattern):
    """Универсальная валидация поля адресса."""
    if not isinstance(value, str):
        logger.warning(f'Передан тип {type(value)}')
        raise serializers.ValidationError('Неверный тип данных в поле')
    value = value.strip()
    if not re.fullmatch(pattern=pattern, string=value):
        message = 'Содержит недопустимые символы.'
        logger.warning(message)
        raise serializers.ValidationError(message)
    return normalize_address(value)


def validate_city_and_street(value):
    """Валидация названия городов и улиц."""
    return validate_field_address(
        value, pattern=constants.PATTERN_CITY_OR_STREET
    )


def validate_house(value):
    """Валидация номера дома."""
    return validate_field_address(
        value, pattern=constants.PATTERN_HOUSE)


def validate_phone(value):
    """Валидация номера телефона."""
    if not value:
        return value
    
    digits = re.sub(constants.PATTERT_DIGITS, '', value)

    if not digits.startswith('+'):
        digits = '+' + digits

    if not re.fullmatch(constants.PATTERN_PHONE, digits):
        logger.warning(f'Некорректный номер телефона {digits}')
        raise serializers.ValidationError(
            'Введите корректный номер телефона.'
        )

    return digits
