from rest_framework.response import Response
from rest_framework import viewsets, generics, permissions
from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework import mixins,viewsets

from .serializers import UserSerializer, RegisterSerializer, CustomTokenObtainPairSerializer
from .permissions import IsManagerOrAdmin,IsAdminRole
from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
)
from rest_framework import status
User = get_user_model()


@extend_schema(tags=['Users Management'])
class UserViewSet(mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
   

    queryset = User.objects.all()

    serializer_class = UserSerializer

    permission_classes = [IsManagerOrAdmin]


    @extend_schema(request=None)
    @action(detail=True,methods=['post'],url_path='assign-manager',permission_classes=[IsAdminRole])
    def assign_manager(self,request,pk=None):
        user = self.get_object()
        user.role = User.Role.MANAGER
        user.save()
        return Response(
            {"detail": f"Foydalanuvchi {user.username} Manager rolini oldi."},
            status=status.HTTP_200_OK
        )



@extend_schema(tags=['Authentication'])
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


@extend_schema(tags=['Authentication'])
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


