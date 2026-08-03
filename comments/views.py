from rest_framework import viewsets, permissions
from .models import Comment
from .serializers import CommentSerializer
from .permissions import IsTaskRelatedUser, IsCommentOwnerOrAdmin
from drf_spectacular.utils import extend_schema


@extend_schema(tags=['Comments'])
class CommentViewSet(viewsets.ModelViewSet):
    """Izohlar uchun CRUD"""
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsTaskRelatedUser, IsCommentOwnerOrAdmin]

    def get_queryset(self):
        """
        Foydalanuvchi faqat o'ziga aloqador tasklarning commentlarini ko'radi:
        - Admin: barcha commentlar
        - Manager: o'z loyihalaridagi tasklarning commentlari
        - Employee: o'ziga tayinlangan yoki o'zi yaratgan tasklarning commentlari
        """
        if getattr(self, 'swagger_fake_view', False):
            return Comment.objects.none()

        user = self.request.user

        if user.role == 'admin':
            return Comment.objects.all()

        if user.role == 'manager':
            return Comment.objects.filter(
                task__project__manager=user
            ) | Comment.objects.filter(
                task__creator=user
            ) | Comment.objects.filter(
                author=user
            )

        # Employee — faqat o'ziga aloqador tasklar
        return Comment.objects.filter(
            task__assignee=user
        ) | Comment.objects.filter(
            task__creator=user
        ) | Comment.objects.filter(
            author=user
        )

    def perform_create(self, serializer):
        # izoh yozgan foydalanuvchini avtomatik biriktirish
        serializer.save(author=self.request.user)
