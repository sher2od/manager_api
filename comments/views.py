from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from .models import Comment
from .serializers import CommentSerializer
from .permissions import IsTaskRelatedUser, IsCommentOwnerOrAdmin


@extend_schema(tags=['Comments'])
class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsTaskRelatedUser, IsCommentOwnerOrAdmin]

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['task']
    ordering_fields = ['created_at']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Comment.objects.none()

        user = self.request.user

        if user.role == 'admin' or user.is_superuser:
            return Comment.objects.select_related('author', 'task').all()

        if user.role == 'manager':
            return Comment.objects.select_related('author', 'task').filter(
                task__project__manager=user
            ) | Comment.objects.filter(
                task__creator=user
            ) | Comment.objects.filter(
                author=user
            )

        return Comment.objects.select_related('author', 'task').filter(
            task__assignee=user
        ) | Comment.objects.filter(
            task__creator=user
        ) | Comment.objects.filter(
            author=user
        )

    def perform_create(self, serializer): 
        serializer.save(author=self.request.user)

