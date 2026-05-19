from rest_framework import serializers

from reviews.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для управления отзывами."""

    author = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score')

    def validate(self, attrs):
        """
        Проверяет,
        что на клинику можно оставить только один отзыва от пользователя.
        """
        request = self.context['request']
        if request.method == 'POST':
            clinic_id = self.context['view'].kwargs.get('clinic_id')
            author = request.user
            if author.reviews.filter(clinic_id=clinic_id).exists():
                raise serializers.ValidationError(
                    'Вы уже оставили отзыв'
                )
        return attrs