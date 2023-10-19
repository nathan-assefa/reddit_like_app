from rest_framework import permissions
from base.api.models import Post, Comment


class IsAuthenticatedUser(permissions.BasePermission):
    def has_permission(self, request, view):
        # Allow all users to view posts
        if request.method == 'GET':
            return True

        return request.user.is_authenticated


class IsCommnentOwner(permissions.BasePermission):
    def has_permission(self, request, view):

        if request.method == 'GET':
            return True

        if not request.user.is_authenticated:
            return False

        if request.method in ['PUT', 'PATCH', 'DELETE']:
            # Assuming "pk" is the name used in the URL pattern
            comment_id = view.kwargs.get('pk')
            try:
                comment = Comment.objects.get(id=comment_id)
                return request.user == comment.author
            except comment.DoesNotExist:
                return False
