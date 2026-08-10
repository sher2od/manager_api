from rest_framework import permissions
from tasks.models import Task


class IsTaskRelatedUser(permissions.BasePermission):
    message = "Siz ushbu vazifaga izoh yozish huquqiga ega emassiz."

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        # Admin har doim ruxsat oladi
        if user.role == 'admin' or user.is_superuser:
            return True

        if request.method in permissions.SAFE_METHODS:
            return True

        if request.method == 'POST':
            task_id = request.data.get('task')
            if not task_id:
                return False

            try:
                task = Task.objects.select_related('project').get(id=task_id)
            except (Task.DoesNotExist, ValueError, TypeError):
                self.message = "Vazifa topilmadi."
                return False

            return (
                task.assignee == user
                or task.creator == user
                or task.project.manager == user
            )

        return True


class IsCommentOwnerOrAdmin(permissions.BasePermission):
    message = "Faqat o'zingiz yozgan izohni tahrirlashingiz yoki o'chirishingiz mumkin."

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        user = request.user
        return (
            obj.author == user
            or user.role == 'admin'
            or user.is_superuser
            or (user.role == 'manager' and obj.task.project.manager == user)
        )

