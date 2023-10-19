from rest_framework import permissions
from base.api.models import Community  # Import your Community model


class CommunityPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in ['GET']:
            # Allow all users to view communities
            return True

        if not request.user.is_authenticated:
            # Deny POST, PUT, PATCH, DELETE to unauthenticated users
            return False

        if request.method == 'POST':
            # Allow authenticated users to create communities
            return True

        # For PUT, PATCH, DELETE, check if the user is the owner of the community
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            # Assuming "pk" is the name used in the URL pattern
            community_id = view.kwargs.get('pk')
            try:
                community = Community.objects.get(id=community_id)
                return request.user == community.owner
            except Community.DoesNotExist:
                return False

        return False
