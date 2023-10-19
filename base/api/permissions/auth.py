from rest_framework import permissions


class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow read-only access for unauthenticated users.
    """

    def has_permission(self, request, view):
        # Allow GET requests for all users
        if request.method == 'GET':
            return True

        # Check for authentication for other request methods
        return request.user and request.user.is_authenticated
