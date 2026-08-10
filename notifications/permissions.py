from rest_framework import permissions


class IsNotificationOwner(permissions.BasePermission):
    """
    Bildirishnomani faqat uning egasi (user) o'qishi yoki o'chirishi mumkin.
    Admin barchasini ko'ra oladi.
    """
    message = "Sizda ushbu bildirishnomaga kirish huquqi yo'q."

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        return obj.user == user or user.role == 'admin' or user.is_superuser
