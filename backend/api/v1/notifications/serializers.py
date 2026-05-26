from rest_framework import serializers

from notifications.models import FCMDevice, UserNotificationSettings


class FCMDeviceSerializer(serializers.ModelSerializer):
    """Сериализатор для сохраниения токена."""

    class Meta:
        model = FCMDevice
        fields = ('id', 'token', 'platform')

class NotificationSettingsSerializer(serializers.ModelSerializer):
    """Сериализатор для управления уведомлениями."""

    class Meta:
        model = UserNotificationSettings
        fields = ('email_enabled', 'push_enabled')
