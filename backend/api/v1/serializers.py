from rest_framework import serializers

from . import validators


class BaseImageSerializer(serializers.ModelSerializer):
    
    image_field = None

    def validate(self, attrs):
        field = self.image_field
        file = attrs.get(field)
        validators.validation_image(file)
        return super().validate(attrs)

    def update(self, instance, validated_data):
        field_name = self.image_field

        old_file = getattr(instance, field_name)
        new_file = validated_data.get(field_name)

        if old_file and old_file != new_file:
            old_file.delete(save=False)

        setattr(instance, field_name, new_file)
        instance.save(update_fields=[field_name])

        return instance