from rest_framework import permissions
from tasks.models import Task


class IsTaskRelatedUser(permissions.BasePermission):
    """
    Comment yozish uchun foydalanuvchi taskga aloqador bo'lishi kerak:
    - Task assignee (vazifa tayinlangan odam)
    - Task creator (vazifani yaratgan odam)
    - Project manager (loyiha menejeri)
    - Admin (har doim ruxsat)
    """
    message = "Sizda ushbu harakatni bajarish uchun ruxsat yo'q."

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        # Admin har doim ruxsat
        if user.role == 'admin':
            return True

        # GET (list) uchun ruxsat
        if request.method in permissions.SAFE_METHODS:
            return True

        # POST (comment yaratish) uchun task_id ni tekshiramiz
        if request.method == 'POST':
            task_id = request.data.get('task')
            if not task_id:
                return False

            try:
                task = Task.objects.select_related('project').get(id=task_id)
            except Task.DoesNotExist:
                self.message = "Vazifa topilmadi."
                return False

            return (
                task.assignee == user          # vazifa tayinlangan odam
                or task.creator == user         # vazifani yaratgan odam
                or task.project.manager == user # loyiha menejeri
            )

        return True


class IsCommentOwnerOrAdmin(permissions.BasePermission):
    """
    Comment'ni faqat o'zi yozgan foydalanuvchi yoki Admin tahrirlashi/o'chirishi mumkin.
    """
    message = "Faqat o'zingiz yozgan izohni tahrirlashingiz yoki o'chirishingiz mumkin."

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return (
            obj.author == request.user
            or request.user.role == 'admin'
        )
