from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Allow everyone to read, but allow only owners to edit/delete
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user
