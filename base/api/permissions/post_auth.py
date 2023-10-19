from rest_framework import permissions
from base.api.models import Community, Post


class IsCommunityMemberOrOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        # Allow all users to view posts
        if request.method == 'GET':
            return True

        if not request.user.is_authenticated:
            return False

        community_id = view.kwargs.get('community_id')

        try:
            # Check if the user is the owner of the community or a member of the community
            community = Community.objects.get(id=community_id)
            return request.user == community.owner or request.user in community.members.all()
        except Community.DoesNotExist:
            return False


class IsPostOwner(permissions.BasePermission):
    def has_permission(self, request, view):

        if request.method == 'GET':
            return True

        if not request.user.is_authenticated:
            return False

        if request.method in ['PUT', 'PATCH', 'DELETE']:
            # Assuming "pk" is the name used in the URL pattern
            post_id = view.kwargs.get('pk')
            try:
                post = Post.objects.get(id=post_id)
                return request.user == post.author
            except post.DoesNotExist:
                return False

    # def has_object_permission(self, request, view, obj):
    #     # Check if the user is the author of the post
    #     return request.user == obj.author
