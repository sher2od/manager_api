from rest_framework import permissions


class IsAdminRole(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'admin'
        )


class IsManagerRole(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user 
            and request.user.is_authenticated 
            and request.user.role == 'manager'
        )



class IsEmployeeRole(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user 
            and request.user.is_authenticated 
            and request.user.role == 'employee'
        )


class IsManagerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user 
            and request.user.is_authenticated 
            and request.user.role in ['admin', 'manager']
        )
