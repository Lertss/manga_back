from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit or delete it.

    Allows read-only access for any user.
    """

    def has_object_permission(self, request, view, obj):
        """
        Checks if the requesting user has permission to access the object.

        Args:
            request: The HTTP request object.
            view: The view being accessed.
            obj: The object being accessed.

        Returns:
            bool: True if the user can read or is the owner for write/delete.

        Example:
            IsOwnerOrReadOnly().has_object_permission(request, view, obj)
        """
        # Allow everyone to read, but allow only owners to edit/delete
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user
