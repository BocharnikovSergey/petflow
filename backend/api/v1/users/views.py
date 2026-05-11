
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import status, generics, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    AvatarSerializer, SignUpSerializer, LoginSerializer,
    TokenResponseSerializer, UserSerializer
)


User = get_user_model()


class SignUpView(generics.CreateAPIView):
    serializer_class = SignUpSerializer
    permission_classes = [AllowAny]


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    @extend_schema(responses=TokenResponseSerializer)
    def post(self, request):
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


# Написать права доступа.
class UserViewSet(viewsets.ModelViewSet):

    queryset = User.objects.prefetch_related('pets')
    # permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    http_method_names = ['get', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action == 'avatar':
            return AvatarSerializer
        return super().get_serializer_class()

    @action(
        detail=False,
        methods=['get'],
    )
    def me(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @me.mapping.patch
    def update_me(self, request):
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
        permission_classes=(IsAuthenticated,),
        url_path='me/avatar'
    )
    def avatar(self, request):
        user = request.user
        serializer = self.get_serializer(user, data=request.data,  partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @avatar.mapping.delete
    def delete_avatar(self, request):
        user = request.user
        if not user.avatar:
            return Response(
                {'detail': 'Нет аватара.'}, status.HTTP_400_BAD_REQUEST
            )

        user.avatar.delete(save=True)
        return Response(
            {'detail': 'Аватар успешно удален.'},
            status=status.HTTP_204_NO_CONTENT
        )