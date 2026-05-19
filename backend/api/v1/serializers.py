from rest_framework import serializers

from . import validators


class BaseImageSerializer(serializers.ModelSerializer):
    """
    Базовый сериализатор для моделей с полем изображения
    (например, логотип, аватар).
    """
    
    image_field = None

    def validate(self, attrs):
        """"Проверяет загружаемый файл через validation_image."""
        field = self.image_field
        file = attrs.get(field)
        validators.validation_image(file)
        return super().validate(attrs)

    def update(self, instance, validated_data):
        """
        Обновляет поле изображения, удаляя старый файл, если он был заменён.
        """
        field_name = self.image_field

        old_file = getattr(instance, field_name)
        new_file = validated_data.get(field_name)

        if old_file and old_file != new_file:
            old_file.delete(save=False)

        setattr(instance, field_name, new_file)
        instance.save(update_fields=[field_name])

        return instance