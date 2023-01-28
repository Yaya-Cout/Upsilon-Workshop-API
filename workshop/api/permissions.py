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
        is_script_admin = is_admin or is_owner
        if is_script_admin:
            return True

        # If the user is not the owner of the script, we need to check if the
        # user is in the list of collaborators of the script
        is_collaborator = request.user in obj.collaborators.all()
        if is_collaborator:
            # Disallow DELETE requests for collaborators
            if request.method in ['DELETE']:
                return False

            # Disallow changing the collaborators list for collaborators
            if (
                request.method in ['PATCH', 'PUT']
                and 'collaborators' in request.data
            ):
                data = dict(request.data.copy())
                # Get the list of collaborators from the request
                collaborators = data['collaborators']

                # Convert the list of collaborators from the request to a list
                # if this is not already the case
                if not isinstance(collaborators, list):
                    collaborators = [collaborators]

                # Get the list of collaborators from the database
                collaborators_db = list(obj.collaborators.all().values_list(
                    'id', flat=True
                ))

                # Convert the list of collaborators from the database to a list
                # of str ids
                collaborators_db = [str(collaborator) for collaborator in
                                    collaborators_db]

                # Convert the list of collaborators from the request to a list
                # of ids
                collaborators = [collaborator.split('/')[-2]
                                 for collaborator in collaborators]

                # Check if the list of collaborators is the same
                if collaborators != collaborators_db:
                    return False

            return True

        # If the user is not the owner of the script, and is not a collaborator,
        # allow read-only access
        return request.method in SAFE_METHODS


class IsRatingOwnerOrReadOnly(BasePermission):
    """Allow read/write permissions to the owner of the object and admin."""

    def has_object_permission(self, request, view: object, obj: object) -> bool:
        """Check if the user has permission to access the object."""
        is_admin = request.user and request.user.is_staff
        is_owner = obj.user == request.user
        is_allowed = is_admin or is_owner

        return request.method in SAFE_METHODS or is_allowed
