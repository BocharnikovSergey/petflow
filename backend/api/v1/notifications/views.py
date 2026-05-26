from rest_framework import generics

from .serializers import FCMDeviceSerializer, NotificationSettingsSerializer
from ..permissions import IsOwner
from notifications.models import FCMDevice


class SaveFCMTokenView(generics.CreateAPIView):
    """Vie для сохранинеия FCM токена."""

    serializer_class = FCMDeviceSerializer
    permission_classes = [IsOwner]

    def perform_create(self, serializer):
        token = serializer.validated_data['token']
        platform = serializer.validated_data['platform']

        FCMDevice.objects.update_or_create(
            token=token,
            defaults={
                'user': self.request.user,
                'platform': platform,
                'is_active': True,
            }
        )


class NotificationSettingsView(generics.RetrieveUpdateAPIView):
    """Vie для управления уведомлениями."""

    serializer_class = NotificationSettingsSerializer
    permission_classes = [IsOwner]
    http_method_names = ['get', 'patch']

    def get_object(self):
        return self.request.user.notification_settings
