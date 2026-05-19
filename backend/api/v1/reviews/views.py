from rest_framework import viewsets

from .serializers import ReviewSerializer
from ..permissions import IsOwnerOrReadOnly
from ..mixins import ClinicMixin


class ReviewViewSet(ClinicMixin, viewsets.ModelViewSet):
    """VieSet для работы с отзывами на клинику."""

    serializer_class = ReviewSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        """
        Возвращает все отзывы текущей клиники с подгрузкой связанных авторов.
        """
        return self.get_clinic().reviews.select_related('author')

    def perform_create(self, serializer):
        """Сохраняет отзыв текущей клиники от текущего пользователя."""
        serializer.save(clinic=self.get_clinic(), author=self.request.user)
