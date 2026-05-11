from rest_framework import serializers
from PIL import Image

from api.v1 import constants


def validation_name(value):
        if not isinstance(value, str):
            raise serializers.ValidationError(constants.ERROR_INVALID_NAME)
         
        value = value.strip()
        if not value or len(value) < constants.MIN_LEN_NAME:
            raise serializers.ValidationError(constants.ERROR_INVALID_NAME)
        
        return value.strip()


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
            if img.format not in constants.IMAGE_FORMAT:
                raise serializers.ValidationError(
                    f'Разрешен формат: {", ".join(constants.IMAGE_FORMAT)}'
                )
    return file