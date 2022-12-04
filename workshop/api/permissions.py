"""Custom permissions check for Upsilon Workshop."""
from rest_framework.permissions import BasePermission, IsAdminUser, SAFE_METHODS


class IsAdminOrReadOnly(IsAdminUser):
    """Allow write permissions to admin users, and read for everyone else."""

    def has_permission(self, request, view: object) -> bool:
        """Check if the user has permission to access the view."""
        is_admin = super().has_permission(request, view)
        return request.method in SAFE_METHODS or is_admin


class ReadWriteWithoutPost(IsAdminUser):
    """Allow read (GET) and write (PUT, PATCH, DELETE), and deny POST."""

    def has_permission(self, request, view: object) -> bool:
        """Check if the user has permission to access the view."""
        is_admin = super().has_permission(request, view)
        return request.method not in ['POST'] or is_admin


class IsOwnerOrReadOnly(BasePermission):
    """Allow read/write permissions to the owner of the object and admin."""

    def has_object_permission(self, request, view: object, obj: object) -> bool:
        """Check if the user has permission to access the object."""
        is_admin = request.user and request.user.is_staff
        is_owner = obj == request.user
        is_allowed = is_admin or is_owner
        return request.method in SAFE_METHODS or is_allowed


class IsScriptOwnerOrReadOnly(BasePermission):
    """Allow read/write permissions to the owner of the object and admin."""

    def has_object_permission(self, request, view: object, obj: object) -> bool:
        """Check if the user has permission to access the object."""
        is_admin = request.user and request.user.is_staff

        # To check if the user is the owner of the script, we need to check if
        # the user is in the list of authors of the script
        is_owner = request.user == obj.author
        is_allowed = is_admin or is_owner
        return request.method in SAFE_METHODS or is_allowed


class IsRatingOwnerOrReadOnly(BasePermission):
    """Allow read/write permissions to the owner of the object and admin."""

    def has_object_permission(self, request, view: object, obj: object) -> bool:
        """Check if the user has permission to access the object."""
        is_admin = request.user and request.user.is_staff
        is_owner = obj.user == request.user
        is_allowed = is_admin or is_owner

        return request.method in SAFE_METHODS or is_allowed
