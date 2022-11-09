"""Custom permissions check for Upsilon Workshop."""
from rest_framework.permissions import IsAdminUser, SAFE_METHODS


class IsAdminOrReadOnly(IsAdminUser):
    """Allow write permissions to admin users, and read for everyone else."""

    def has_permission(self, request, view: object) -> bool:
        """Check if the user has permission to access the view."""
        is_admin = super().has_permission(request, view)
        return request.method in SAFE_METHODS or is_admin
