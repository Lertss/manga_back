from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Дозволити читати всім, але дозволити редагувати/видаляти тільки власникам
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user
