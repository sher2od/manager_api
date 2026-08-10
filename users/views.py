from django.http import request
from rest_framework import generics, permissions, status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_spectacular.utils import extend_schema


from .serializers import RegisterSerializer, CustomTokenObtainPairSerializer, UserSerializer
from .permissions import IsManagerOrAdmin,IsAdminRole

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

    @action(
        detail=False,
        methods=['get', 'put', 'patch'],
        permission_classes=[permissions.IsAuthenticated],
        url_path='me'
    )
    def me(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        partial = (request.method == 'PATCH')
        serializer = self.get_serializer(user, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(request=None)
    @action(
        detail=True,
        methods=['post'],
        url_path='assign-manager',
        permission_classes=[IsAdminRole]
    )
    def assign_manager(self, request, pk=None):
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
    throttle_classes = [AnonRateThrottle]

    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    throttle_classes = [AnonRateThrottle]


@extend_schema(tags=['Authentication'])
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    throttle_classes = [AnonRateThrottle]








































