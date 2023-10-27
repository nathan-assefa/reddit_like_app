from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import permissions
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, ListAPIView, ListCreateAPIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from django.contrib.auth.models import User

from base.api.Custom_views.message import (
    SendMessageView,
    GetUserMessagesView,
    MarkMessageAsReadView,
    ClearUnreadMessagesCount,
    GetMostRecentMessageView
)

from base.api.Custom_views.notifications import (
    GetUserNotification,
    MarkNotificationAsRead
)
from base.api.Custom_views.profile import (
    GetUserProfile,
    UpdateProfile,
    ToggleFollowUserAPIView,
    GetProfileList,
    FollowStateAPIView
)

from base.api.Custom_views.community import (
    CommunityList,
    CommunityDetail,
    CommunityListForOwnerOrMember,
    TopCommunitiesView,
    JoinOrLeaveCommunityView,
    CommunityMembershipStatusView
)

from base.api.Custom_views.post import (
    CommunityPostList,
    PostDetail,
    PostList
)

from base.api.Custom_views.comment import (
    CommentList,
    CommentDetail
)

from .serializers import (
    BookMarksSerializer,
)

from .models import (
    Comment,
    BookMarks,
    CommentLike,
    CommentLove,
    CommentUpvoted,
    CommentDownvoted,
    Post,
    PostLike,
    PostLove,
    PostUpvoted,
    PostDownvoted,
)


from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['notification_count'] = user.profile.unread_notifications_count
        print(token['notification_count'])

        return token


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_bookmarks(request, user_id):
    try:
        bookmarks = BookMarks.objects.filter(user_id=user_id)
    except BookMarks.DoesNotExist:
        return Response({'error': 'Bookmarks not found for this user'}, status=404)

    serializer = BookMarksSerializer(bookmarks, many=True)
    return Response(serializer.data, status=200)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_bookmark(request):
    post_id = request.data.get('post_id')

    # Check if the post exists
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return Response({'error': 'Post not found'}, status=404)

    # Check if a bookmark for this post already exists for the user
    existing_bookmark = BookMarks.objects.filter(
        user=request.user, post=post).first()

    if existing_bookmark:
        return Response({'message': 'This post is already bookmarked'}, status=400)

    # Create a new bookmark
    bookmark = BookMarks.objects.create(
        user=request.user,
        post=post
    )

    serializer = BookMarksSerializer(bookmark)
    return Response(serializer.data, status=201)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_bookmark(request, bookmark_id):
    try:
        bookmark = BookMarks.objects.get(id=bookmark_id, user=request.user)
    except BookMarks.DoesNotExist:
        return Response({'error': 'Bookmark not found'}, status=404)

    bookmark.delete()
    return Response({'message': 'Bookmark deleted successfully'}, status=204)


""" Handling post reactions """


class LikePost(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, post_id, format=None):
        user = request.user
        post = get_object_or_404(Post, pk=post_id)

        existing_like = PostLike.objects.filter(user=user, post=post).first()

        if existing_like:
            existing_like.delete()
            liked = False
        else:
            PostLike.objects.create(user=user, post=post)
            liked = True

        return Response({'liked': liked}, status=status.HTTP_200_OK)


class LovePost(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, post_id, format=None):
        user = request.user
        post = get_object_or_404(Post, pk=post_id)

        existing_love = PostLove.objects.filter(user=user, post=post).first()

        if existing_love:
            existing_love.delete()
            loved = False
        else:
            PostLove.objects.create(user=user, post=post)
            loved = True

        return Response({'loved': loved}, status=status.HTTP_200_OK)


class UpvotePost(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, post_id, format=None):
        user = request.user
        post = get_object_or_404(Post, pk=post_id)

        existing_upvote = PostUpvoted.objects.filter(
            user=user, post=post).first()

        if existing_upvote:
            existing_upvote.delete()
            upvoted = False
        else:
            existing_downvote = PostDownvoted.objects.filter(
                user=user, post=post).first()
            if existing_downvote:
                existing_downvote.delete()
            PostUpvoted.objects.create(user=user, post=post)
            upvoted = True

        return Response({'upvoted': upvoted}, status=status.HTTP_200_OK)


class DownvotePost(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, post_id, format=None):
        user = request.user
        post = get_object_or_404(Post, pk=post_id)

        existing_downvote = PostDownvoted.objects.filter(
            user=user, post=post).first()

        if existing_downvote:
            existing_downvote.delete()
            downvoted = False
        else:
            existing_upvote = PostUpvoted.objects.filter(
                user=user, post=post).first()
            if existing_upvote:
                existing_upvote.delete()
            PostDownvoted.objects.create(user=user, post=post)
            downvoted = True

        return Response({'downvoted': downvoted}, status=status.HTTP_200_OK)


""" Handling comment reactions """


class LikeComment(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, comment_id, format=None):
        user = request.user

        comment = get_object_or_404(Comment, pk=comment_id)
        existing_like = CommentLike.objects.filter(
            user=user, comment=comment).first()

        if existing_like:
            existing_like.delete()
            liked = False
        else:
            CommentLike.objects.create(user=user, comment=comment)
            liked = True

        return Response({'liked': liked}, status=status.HTTP_200_OK)


class LoveComment(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, comment_id, format=None):
        user = request.user

        comment = get_object_or_404(Comment, pk=comment_id)
        existing_love = CommentLove.objects.filter(
            user=user, comment=comment).first()

        if existing_love:
            existing_love.delete()
            loved = False
        else:
            CommentLove.objects.create(user=user, comment=comment)
            loved = True

        return Response({'loved': loved}, status=status.HTTP_200_OK)


class UpvoteComment(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, comment_id, format=None):
        user = request.user

        comment = get_object_or_404(Comment, pk=comment_id)
        existing_upvote = CommentUpvoted.objects.filter(
            user=user, comment=comment).first()

        if existing_upvote:
            existing_upvote.delete()
            upvoted = False
        else:
            existing_downvote = CommentDownvoted.objects.filter(
                user=user, comment=comment).first()
            if existing_downvote:
                existing_downvote.delete()
            CommentUpvoted.objects.create(user=user, comment=comment)
            upvoted = True

        return Response({'upvoted': upvoted}, status=status.HTTP_200_OK)


class DownvoteComment(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, comment_id, format=None):
        user = request.user

        comment = get_object_or_404(Comment, pk=comment_id)
        existing_downvote = CommentDownvoted.objects.filter(
            user=user, comment=comment).first()

        if existing_downvote:
            existing_downvote.delete()
            downvoted = False
        else:
            existing_upvote = CommentUpvoted.objects.filter(
                user=user, comment=comment).first()
            if existing_upvote:
                existing_upvote.delete()
            CommentDownvoted.objects.create(user=user, comment=comment)
            downvoted = True

        return Response({'downvoted': downvoted}, status=status.HTTP_200_OK)


class ClearUnreadNotificationsCount(APIView):
    def post(self, request):
        user = request.user
        user.profile.unread_notifications_count = 0
        user.profile.save()
        return Response({'message': 'Unread notification count cleared.'}, status=status.HTTP_200_OK)
