
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import status, generics, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    AvatarSerializer, SignUpSerializer, LoginSerializer,
    TokenResponseSerializer, UserSerializer
)
from ..permissions import IsOwner, IsAdminOrReadOnly
from ..mixins import ActionReadWriteSerializerMixin, ImageActionMixin


User = get_user_model()


class SignUpView(generics.CreateAPIView):
    """Представление для регистрации нового пользователя."""
    serializer_class = SignUpSerializer
    permission_classes = [AllowAny]


class LoginView(generics.GenericAPIView):
    """Представление для аутентификации пользователя (входа)."""

    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    @extend_schema(responses=TokenResponseSerializer)
    def post(self, request):
        """Обрабатывает POST-запрос на вход."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        user = User.objects.get(email=email)
        token = RefreshToken.for_user(user)
        
        return Response(
            TokenResponseSerializer({
                'access': str(token.access_token),
                'refresh': str(token)
            }).data,
            status=status.HTTP_200_OK
        )


class UserViewSet(
    ActionReadWriteSerializerMixin, ImageActionMixin, viewsets.ModelViewSet
):
    """ViewSet для управления пользователями."""

    queryset = User.objects.prefetch_related('pets')
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = UserSerializer
    http_method_names = ['get', 'patch', 'delete']
    image_field = 'avatar'
    serializer_classes = {'avatar': AvatarSerializer}

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsOwner]
    )
    def me(self, request):
        """Возвращает данные текущего аутентифицированного пользователя."""
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @me.mapping.patch
    def update_me(self, request):
        """Частично обновляет данные текущего пользователя."""
        user = request.user
        serializer = self.get_serializer(
            user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @me.mapping.delete
    def delete_me(self, request):
        user = request.user
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['patch'],
        permission_classes=(IsOwner,),
        url_path='me/avatar'
    )
    def avatar(self, request):
        """
        Обновление аватара пользователя.
        Ожидает multipart/form-data с полем 'avatar'.
        """
        return self._update_image(request.user, request)

    @avatar.mapping.delete
    def delete_avatar(self, request):
        """
        Удаление аватара пользователя.
        Убирает ссылку на файл и удаляет его с диска.
        """
        return self._delete_image(request.user)
