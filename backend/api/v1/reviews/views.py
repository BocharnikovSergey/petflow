from django.shortcuts import get_object_or_404
from rest_framework import viewsets

from .serializers import ReviewSerializer
from ..permissions import IsOwnerOrReadOnly
from clinics.models import Clinic


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с отзывами на произведения."""

    serializer_class = ReviewSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = [IsOwnerOrReadOnly]

    def get_clinic(self):
        """Получает произведение по id из URL."""
        if not hasattr(self, '_clinic'):
            self._clinic = get_object_or_404(
                Clinic, id=self.kwargs.get('clinic_id')
            )
        return self._clinic

    def get_queryset(self):
        return self.get_clinic().reviews.select_related('author')

    def perform_create(self, serializer):
        serializer.save(clinic=self.get_clinic(), author=self.request.user)
